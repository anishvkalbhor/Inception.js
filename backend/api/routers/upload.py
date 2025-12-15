# backend/api/routers/upload.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from pathlib import Path
import asyncio
import shutil
import mimetypes
from datetime import datetime
import threading
import json

# Services
from services.mongodb_service import (
    insert_document,
    get_document_by_hash
)
from services.local_storage_service import compute_bytes_hash
from services.pipeline_orchestrator import UploadPipelineOrchestrator

router = APIRouter()

# ✅ FIXED: Use backend root, then add data/uploads
BACKEND_ROOT = Path(__file__).resolve().parents[2]  # d:\Inception.js\backend
UPLOAD_ROOT = BACKEND_ROOT / "data" / "uploads"

print(f"🔍 Upload Router Initialized:")
print(f"   __file__: {__file__}")
print(f"   BACKEND_ROOT: {BACKEND_ROOT}")
print(f"   UPLOAD_ROOT: {UPLOAD_ROOT}")

orchestrator = UploadPipelineOrchestrator()

# ✅ ADDED: Lock for version calculation to prevent race conditions
_version_lock = threading.Lock()


# ---------------------- Models ----------------------

class UploadResponse(BaseModel):
    document_id: str
    version: int
    status: str


# ---------------------- Helpers ----------------------

def _get_next_version(document_id: str) -> int:
    """Thread-safe version calculation"""
    with _version_lock:
        base = UPLOAD_ROOT / document_id
        if not base.exists():
            return 1
        versions = [
            int(p.name[1:])
            for p in base.iterdir()
            if p.is_dir() and p.name.startswith("v")
        ]
        next_version = max(versions, default=0) + 1
        return next_version


def _safe_doc_id(filename: str) -> str:
    stem = Path(filename).stem
    return stem.replace(" ", "_").replace("/", "_")


# ---------------------- Endpoint ----------------------

@router.post("/", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    org_id: str = Form(""),
    uploader_id: str = Form(""),
    category: str = Form("uploads")
):
    """
    Upload endpoint (pipeline-driven).
    - Saves file to backend/data/uploads
    - Registers DB metadata
    - Triggers vectorDB pipeline
    """

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    filename = Path(file.filename).name
    document_id = _safe_doc_id(filename)
    version = _get_next_version(document_id)

    base_path = UPLOAD_ROOT / document_id / f"v{version}"
    base_path.mkdir(parents=True, exist_ok=True)

    file_bytes = await file.read()
    file_hash = compute_bytes_hash(file_bytes)
    mime_type, _ = mimetypes.guess_type(filename)
    mime_type = mime_type or "application/octet-stream"

    # ---------------- Save file ----------------
    original_path = base_path / "original.pdf"
    original_path.write_bytes(file_bytes)
    
    print(f"✅ File saved to: {original_path}")
    print(f"   File exists: {original_path.exists()}")
    print(f"   File size: {len(file_bytes)} bytes")

    # ---------------- DB record ----------------
    record = {
        "document_id": document_id,
        "version": version,
        "filename": filename,
        "file_hash": file_hash,
        "file_size": len(file_bytes),
        "mime_type": mime_type,
        "category": category,
        "org_id": org_id,
        "uploader_id": uploader_id,
        "upload_path": str(original_path),
        "status": "queued",
        "created_at": datetime.utcnow().isoformat()
    }

    from pymongo.errors import DuplicateKeyError

    try:
        await asyncio.to_thread(insert_document, record)
    except DuplicateKeyError:
        existing = await asyncio.to_thread(get_document_by_hash, file_hash)
        return UploadResponse(
            document_id=existing["document_id"],
            version=existing.get("version", 1),
            status="ALREADY_EXISTS"
        )

    # ---------------- Trigger pipeline ----------------
    print(f"🚀 Triggering pipeline for: {document_id} v{version}")
    orchestrator.enqueue(document_id, version)

    return UploadResponse(
        document_id=document_id,
        version=version,
        status="QUEUED"
    )

@router.get("/{document_id}/status")
async def get_document_status(document_id: str, version: int = 1):
    """
    Get processing status for an uploaded document by reading status.json
    """
    status_path = UPLOAD_ROOT / document_id / f"v{version}" / "status.json"
    
    if not status_path.exists():
        return {
            "document_id": document_id,
            "version": version,
            "stage": "NOT_FOUND",
            "progress_step": 0,
            "ready": False,
            "error": None
        }
    
    try:
        with open(status_path, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
        
        stage = status_data.get("stage", "UNKNOWN")
        error = status_data.get("error")
        
        # Map pipeline stages to progress steps (0-5)
        stage_mapping = {
            "PARSING": 1,
            "CHUNKING": 2,
            "EMBEDDING_DENSE": 3,
            "EMBEDDING_SPARSE": 3,  # Same step as dense
            "INDEXING": 4,
            "READY": 5,
            "FAILED": -1
        }
        
        progress_step = stage_mapping.get(stage, 0)
        ready = (stage == "READY")
        
        return {
            "document_id": document_id,
            "version": version,
            "stage": stage,
            "progress_step": progress_step,
            "ready": ready,
            "error": error,
            "updated_at": status_data.get("updated_at")
        }
    except Exception as e:
        return {
            "document_id": document_id,
            "version": version,
            "stage": "ERROR",
            "progress_step": 0,
            "ready": False,
            "error": str(e)
        }
