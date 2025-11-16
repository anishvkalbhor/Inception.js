from fastapi import APIRouter, Depends, HTTPException
from backend.models.requests import ChatRequest
from backend.models.responses import ChatResponse, SearchResultItem
from backend.services.milvus_service import MilvusService
from backend.services.embedding_service import EmbeddingService
from backend.services.llm_service import LLMService
from backend.api.dependencies import get_milvus_service, get_embedding_service, get_llm_service

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    milvus: MilvusService = Depends(get_milvus_service),
    embedding: EmbeddingService = Depends(get_embedding_service),
    llm: LLMService = Depends(get_llm_service)
):
    """RAG Q&A with citations"""
    try:
        # Generate query embedding
        query_embedding = embedding.embed_text(request.query)
        
        # Search in Milvus
        results = milvus.search(request.collection_name, query_embedding, request.top_k)
        
        # Extract context
        context_chunks = [hit.entity.get("text") for hit in results]
        
        # Generate answer
        answer = await llm.generate_answer(request.query, context_chunks)
        
        # Format sources
        sources = []
        for hit in results:
            sources.append(SearchResultItem(
                document_id=hit.entity.get("document_id"),
                chunk_index=hit.entity.get("chunk_index"),
                text=hit.entity.get("text"),
                page_number=hit.entity.get("page_number"),
                score=hit.distance
            ))
        
        return ChatResponse(answer=answer, sources=sources, query=request.query)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))