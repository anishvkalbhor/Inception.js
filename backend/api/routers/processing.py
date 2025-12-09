from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# CREATE THE ROUTER - This was missing!
router = APIRouter()


class ProcessRequest(BaseModel):
    """Request model for document processing"""
    document_id: str
    operation: str  # e.g., "parse", "chunk", "embed"
    options: Optional[dict] = None


class ProcessResponse(BaseModel):
    """Response model for processing tasks"""
    task_id: str
    status: str
    message: str


# In-memory task storage (replace with Redis/database in production)
processing_tasks = {}


@router.post("/start", response_model=ProcessResponse)
async def start_processing(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a document processing task
    """
    import uuid
    
    task_id = str(uuid.uuid4())
    
    processing_tasks[task_id] = {
        "id": task_id,
        "document_id": request.document_id,
        "operation": request.operation,
        "status": "queued",
        "progress": 0
    }
    
    # Add background task
    background_tasks.add_task(
        process_document,
        task_id,
        request.document_id,
        request.operation,
        request.options or {}
    )
    
    return ProcessResponse(
        task_id=task_id,
        status="queued",
        message=f"Processing task {task_id} started"
    )


@router.get("/status/{task_id}")
async def get_processing_status(task_id: str):
    """
    Get the status of a processing task
    """
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return processing_tasks[task_id]


@router.get("/tasks")
async def list_processing_tasks():
    """
    List all processing tasks
    """
    return {
        "total": len(processing_tasks),
        "tasks": list(processing_tasks.values())
    }


@router.delete("/task/{task_id}")
async def cancel_processing_task(task_id: str):
    """
    Cancel a processing task
    """
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = processing_tasks[task_id]
    
    if task["status"] in ["completed", "failed"]:
        return {
            "message": f"Task {task_id} already {task['status']}"
        }
    
    task["status"] = "cancelled"
    
    return {
        "message": f"Task {task_id} cancelled",
        "task": task
    }


@router.get("/")
async def processing_root():
    """Processing router status"""
    return {
        "message": "Processing router",
        "endpoints": {
            "start": "/start",
            "status": "/status/{task_id}",
            "tasks": "/tasks",
            "cancel": "/task/{task_id}"
        },
        "active_tasks": len([t for t in processing_tasks.values() if t["status"] == "processing"]),
        "total_tasks": len(processing_tasks)
    }


# Background task function
async def process_document(
    task_id: str,
    document_id: str,
    operation: str,
    options: dict
):
    """
    Background task to process a document
    """
    import asyncio
    
    try:
        logger.info(f"Starting processing task {task_id} for document {document_id}")
        
        processing_tasks[task_id]["status"] = "processing"
        processing_tasks[task_id]["progress"] = 0
        
        # Simulate processing with progress updates
        for progress in range(0, 101, 20):
            await asyncio.sleep(1)  # Simulate work
            processing_tasks[task_id]["progress"] = progress
            logger.debug(f"Task {task_id} progress: {progress}%")
        
        processing_tasks[task_id]["status"] = "completed"
        processing_tasks[task_id]["progress"] = 100
        
        logger.info(f"Task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        processing_tasks[task_id]["status"] = "failed"
        processing_tasks[task_id]["error"] = str(e)