from fastapi import APIRouter, Depends, HTTPException
from backend.models.requests import CreateCollectionRequest
from backend.services.milvus_service import MilvusService
from backend.api.dependencies import get_milvus_service

router = APIRouter()

@router.post("/")
async def create_collection(
    request: CreateCollectionRequest,
    milvus: MilvusService = Depends(get_milvus_service)
):
    """Create a new Milvus collection"""
    try:
        collection_name = request.name
        milvus.create_collection(collection_name)
        
        return {
            "collection_name": collection_name,
            "status": "created",
            "description": request.description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_collections(
    milvus: MilvusService = Depends(get_milvus_service)
):
    """List all collections"""
    try:
        collections = milvus.list_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{collection_name}")
async def delete_collection(
    collection_name: str,
    milvus: MilvusService = Depends(get_milvus_service)
):
    """Delete a collection"""
    try:
        success = milvus.delete_collection(collection_name)
        if success:
            return {"message": f"Collection '{collection_name}' deleted"}
        else:
            raise HTTPException(status_code=404, detail="Collection not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))