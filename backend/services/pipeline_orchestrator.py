# backend/services/pipeline_orchestrator.py

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import threading

# ✅ FIXED: Ensure data folder is always inside backend
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # d:\Inception.js
BACKEND_ROOT = PROJECT_ROOT / "backend"
VECTOR_DB_DIR = BACKEND_ROOT / "vectorDB"
BASE_UPLOAD_DIR = BACKEND_ROOT / "data" / "uploads"  # ✅ Inside backend/data

print(f"🔍 Pipeline Orchestrator Initialized:")
print(f"   PROJECT_ROOT: {PROJECT_ROOT}")
print(f"   BACKEND_ROOT: {BACKEND_ROOT}")
print(f"   VECTOR_DB_DIR: {VECTOR_DB_DIR}")
print(f"   BASE_UPLOAD_DIR: {BASE_UPLOAD_DIR}")


def _status_file(base_path: Path) -> Path:
    return base_path / "status.json"


def update_status(base_path: Path, stage: str, error: str | None = None):
    payload = {
        "stage": stage,
        "updated_at": datetime.utcnow().isoformat(),
        "error": error
    }
    status_path = _status_file(base_path)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


class UploadPipelineOrchestrator:
    """
    Orchestrates the document ingestion pipeline using existing scripts:
    - upload_parse.py
    - semantic_chunker.py
    - embedding_creator.py
    - sparse_embedding_creator.py
    - milvus_creator.py
    """

    def __init__(self):
        self.vector_scripts = {
            "parse": VECTOR_DB_DIR / "upload_parse.py",
            "chunk": VECTOR_DB_DIR / "semantic_chunker.py",
            "dense": VECTOR_DB_DIR / "embedding_creator.py",
            "sparse": VECTOR_DB_DIR / "sparse_embedding_creator.py",
            "milvus": VECTOR_DB_DIR / "milvus_creator_upload.py",
        }
        
        # Verify scripts exist
        for name, path in self.vector_scripts.items():
            if not path.exists():
                print(f"⚠️  Warning: {name} script not found: {path}")
        
        # ✅ ADDED: Ensure data directory exists
        BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Upload directory ready: {BASE_UPLOAD_DIR}")

    def enqueue(self, document_id: str, version: int):
        """Fire-and-forget background execution."""
        thread = threading.Thread(
            target=self.run_pipeline,
            args=(document_id, version),
            daemon=True
        )
        thread.start()

    def _run_parse(self, base_path: Path):
        """Runs upload_parse.py in scoped working directory."""
        # ✅ REDUCED: Minimal logging
        result = subprocess.run(
            ["python", str(self.vector_scripts["parse"])],
            cwd=str(base_path),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # ✅ REDUCED: Only log errors
        if result.returncode != 0:
            print(f"❌ Parse failed for {base_path.parent.name}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")  # Limit error output
            raise subprocess.CalledProcessError(
                result.returncode, 
                result.args, 
                output=result.stdout, 
                stderr=result.stderr
            )

    def _run_chunking(self, base_path: Path):
        # ✅ REDUCED: Minimal logging
        result = subprocess.run(
            ["python", str(self.vector_scripts["chunk"])],
            cwd=str(base_path),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print(f"❌ Chunking failed for {base_path.parent.name}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            raise subprocess.CalledProcessError(
                result.returncode, result.args, 
                output=result.stdout, stderr=result.stderr
            )

    def _run_dense_embeddings(self, base_path: Path):
        # ✅ REDUCED: Minimal logging
        result = subprocess.run(
            ["python", str(self.vector_scripts["dense"])],
            cwd=str(base_path),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print(f"❌ Dense embedding failed for {base_path.parent.name}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            raise subprocess.CalledProcessError(
                result.returncode, result.args,
                output=result.stdout, stderr=result.stderr
            )

    def _run_sparse_embeddings(self, base_path: Path):
        # ✅ REDUCED: Minimal logging
        result = subprocess.run(
            ["python", str(self.vector_scripts["sparse"])],
            cwd=str(base_path),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print(f"❌ Sparse embedding failed for {base_path.parent.name}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            raise subprocess.CalledProcessError(
                result.returncode, result.args,
                output=result.stdout, stderr=result.stderr
            )

    def _run_milvus_ingestion(self, base_path: Path):
        # ✅ REDUCED: Minimal logging
        result = subprocess.run(
            ["python", str(self.vector_scripts["milvus"])],
            cwd=str(base_path),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print(f"❌ Milvus ingestion failed for {base_path.parent.name}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            raise subprocess.CalledProcessError(
                result.returncode, result.args,
                output=result.stdout, stderr=result.stderr
            )

    def run_pipeline(self, document_id: str, version: int):
        base_path = BASE_UPLOAD_DIR / document_id / f"v{version}"
        base_path.mkdir(parents=True, exist_ok=True)
        
        # ✅ REDUCED: Single line start message
        print(f"🚀 Pipeline: {document_id} v{version}")

        try:
            update_status(base_path, "PARSING")
            self._run_parse(base_path)

            update_status(base_path, "CHUNKING")
            self._run_chunking(base_path)

            update_status(base_path, "EMBEDDING_DENSE")
            self._run_dense_embeddings(base_path)

            update_status(base_path, "EMBEDDING_SPARSE")
            self._run_sparse_embeddings(base_path)

            update_status(base_path, "INDEXING")
            self._run_milvus_ingestion(base_path)

            update_status(base_path, "READY")
            # ✅ REDUCED: Single line completion message
            print(f"✅ Complete: {document_id} v{version}")

        except subprocess.CalledProcessError as e:
            error_msg = f"Script failed with exit code {e.returncode}"
            print(f"❌ Failed: {document_id} v{version} - {error_msg}")
            update_status(base_path, "FAILED", error_msg)
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"❌ Failed: {document_id} v{version} - {error_msg}")
            update_status(base_path, "FAILED", error_msg)
