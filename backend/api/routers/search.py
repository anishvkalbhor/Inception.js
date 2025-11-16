from fastapi import APIRouter, Depends, HTTPException
from backend.models.requests import SearchRequest
from backend.models.responses import SearchResponse, SearchResultItem
from backend.services.milvus_service import MilvusService
from backend.services.embedding_service import EmbeddingService
from backend.api.dependencies import get_milvus_service, get_embedding_service

router = APIRouter()

@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    milvus: MilvusService = Depends(get_milvus_service),
    embedding: EmbeddingService = Depends(get_embedding_service)
):
    """Vector search in collection"""
    try:
        # Generate query embedding
        query_embedding = embedding.embed_text(request.query)
        
        # Search in Milvus
        results = milvus.search(request.collection_name, query_embedding, request.top_k)
        
        # Format results
        search_results = []
        for hit in results:
            search_results.append(SearchResultItem(
                document_id=hit.entity.get("document_id"),
                chunk_index=hit.entity.get("chunk_index"),
                text=hit.entity.get("text"),
                page_number=hit.entity.get("page_number"),
                score=hit.distance
            ))
        
        return SearchResponse(results=search_results, query=request.query)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))