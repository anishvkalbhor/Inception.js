# backend/services/google_drive_service.py

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from typing import List, Dict, Optional, Any
import io
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
load_dotenv(env_file)

# Lazy initialization
_drive_service = None


def get_drive_service():
    """
    Initialize Google Drive API service
    
    Uses service account credentials for authentication.
    Set GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE in .env to path of JSON key file.
    """
    global _drive_service
    
    if _drive_service is None:
        # Path to service account credentials JSON file
        creds_file = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE")
        
        if not creds_file:
            raise ValueError(
                "GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE environment variable is required. "
                "Download service account JSON from Google Cloud Console."
            )
        
        if not os.path.exists(creds_file):
            raise FileNotFoundError(f"Service account file not found: {creds_file}")
        
        # Create credentials from service account file
        scopes = ['https://www.googleapis.com/auth/drive.readonly']
        creds = service_account.Credentials.from_service_account_file(
            creds_file, scopes=scopes
        )
        
        _drive_service = build('drive', 'v3', credentials=creds)
        print(f"Google Drive service initialized with service account: {creds_file}")
    
    return _drive_service


def list_files_in_folder(folder_id: str, page_size: int = 100) -> List[Dict[str, Any]]:
    """
    List all files in a Google Drive folder (non-recursive)
    
    Returns list of file metadata dictionaries with:
    - id: Google Drive file ID
    - name: filename
    - mimeType: MIME type
    - size: file size in bytes (if available)
    - modifiedTime: last modified timestamp
    - md5Checksum: MD5 hash (if available)
    """
    service = get_drive_service()
    
    query = f"'{folder_id}' in parents and trashed=false"
    fields = "nextPageToken, files(id, name, mimeType, size, modifiedTime, md5Checksum, parents)"
    
    files = []
    page_token = None
    
    while True:
        try:
            response = service.files().list(
                q=query,
                pageSize=page_size,
                fields=fields,
                pageToken=page_token
            ).execute()
            
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken')
            
            if not page_token:
                break
                
        except Exception as e:
            print(f"Error listing files in folder {folder_id}: {e}")
            raise
    
    print(f"Found {len(files)} files in folder {folder_id}")
    return files


def list_files_recursive(folder_id: str, path_prefix: str = "") -> List[Dict[str, Any]]:
    """
    Recursively list all files in a Google Drive folder and subfolders
    
    Returns list of file metadata with added 'drive_path' field showing relative path
    Handles errors gracefully by skipping inaccessible folders
    """
    service = get_drive_service()
    all_files = []
    
    def _recurse(fid: str, prefix: str):
        try:
            items = list_files_in_folder(fid)
        except Exception as e:
            print(f"Warning: Skipping folder {fid} due to error: {e}")
            return  # Skip this folder and continue with others
        
        for item in items:
            mime_type = item.get('mimeType', '')
            item_name = item.get('name', '')
            
            # Build relative path
            current_path = f"{prefix}/{item_name}" if prefix else item_name
            item['drive_path'] = current_path
            
            if mime_type == 'application/vnd.google-apps.folder':
                # It's a folder - recurse into it
                try:
                    _recurse(item['id'], current_path)
                except Exception as e:
                    print(f"Warning: Skipping subfolder {item_name} due to error: {e}")
                    continue  # Skip this subfolder and continue with siblings
            else:
                # It's a file - add to results
                all_files.append(item)
    
    _recurse(folder_id, path_prefix)
    print(f"Found {len(all_files)} files recursively in folder {folder_id}")
    return all_files


def download_file(file_id: str, destination_path: Path) -> bool:
    """
    Download a file from Google Drive to local path
    
    Args:
        file_id: Google Drive file ID
        destination_path: Local Path object where file should be saved
        
    Returns:
        True if download successful, False otherwise
    """
    service = get_drive_service()
    
    try:
        # Ensure parent directory exists
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Request file download
        request = service.files().get_media(fileId=file_id)
        
        # Download file in chunks
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download progress: {int(status.progress() * 100)}%", end='\r')
        
        # Write to destination
        destination_path.write_bytes(fh.getvalue())
        print(f"\nDownloaded: {destination_path}")
        return True
        
    except Exception as e:
        print(f"Error downloading file {file_id}: {e}")
        return False


def get_file_metadata(file_id: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata for a single file
    
    Returns file metadata dictionary or None if error
    """
    service = get_drive_service()
    
    try:
        fields = "id, name, mimeType, size, modifiedTime, md5Checksum, parents"
        file_meta = service.files().get(fileId=file_id, fields=fields).execute()
        return file_meta
    except Exception as e:
        print(f"Error getting metadata for file {file_id}: {e}")
        return None


def get_folder_structure(folder_id: str) -> Dict[str, Any]:
    """
    Get complete folder structure with file counts and metadata
    
    Returns nested dictionary representing folder hierarchy
    """
    service = get_drive_service()
    
    def _build_tree(fid: str, name: str = "root") -> Dict[str, Any]:
        items = list_files_in_folder(fid)
        
        node = {
            "name": name,
            "id": fid,
            "files": [],
            "folders": [],
            "file_count": 0,
            "total_size": 0
        }
        
        for item in items:
            mime_type = item.get('mimeType', '')
            
            if mime_type == 'application/vnd.google-apps.folder':
                # Recurse into subfolder
                subfolder = _build_tree(item['id'], item['name'])
                node['folders'].append(subfolder)
                node['file_count'] += subfolder['file_count']
                node['total_size'] += subfolder['total_size']
            else:
                # It's a file
                file_size = int(item.get('size', 0))
                node['files'].append({
                    "id": item['id'],
                    "name": item['name'],
                    "size": file_size,
                    "modified": item.get('modifiedTime'),
                    "mime_type": mime_type
                })
                node['file_count'] += 1
                node['total_size'] += file_size
        
        return node
    
    return _build_tree(folder_id)


def get_changes_since(start_page_token: str) -> List[Dict[str, Any]]:
    """
    Get changes to files since a specific page token
    
    This can be used for incremental sync to only fetch files that changed.
    Note: Requires setting up change notifications and tracking page tokens.
    
    Args:
        start_page_token: Token from previous sync
        
    Returns:
        List of changed files
    """
    service = get_drive_service()
    
    changes = []
    page_token = start_page_token
    
    try:
        while page_token is not None:
            response = service.changes().list(
                pageToken=page_token,
                spaces='drive',
                fields='nextPageToken, newStartPageToken, changes(fileId, file(id, name, mimeType, size, modifiedTime, md5Checksum))'
            ).execute()
            
            for change in response.get('changes', []):
                if change.get('file'):
                    changes.append(change['file'])
            
            page_token = response.get('nextPageToken')
            
            if 'newStartPageToken' in response:
                # Save this for next sync
                print(f"New page token: {response['newStartPageToken']}")
        
        return changes
        
    except Exception as e:
        print(f"Error fetching changes: {e}")
        return []


def get_start_page_token() -> Optional[str]:
    """
    Get the current page token for starting change tracking
    
    Call this once to get initial token, then use get_changes_since() for incremental sync
    """
    service = get_drive_service()
    
    try:
        response = service.changes().getStartPageToken().execute()
        return response.get('startPageToken')
    except Exception as e:
        print(f"Error getting start page token: {e}")
        return None
