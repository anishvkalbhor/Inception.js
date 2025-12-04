from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="User query text", min_length=1)
    top_k: Optional[int] = Field(3, description="Number of results to retrieve", ge=1, le=10)

class SearchResult(BaseModel):
    text: str
    source: str
    page: int
    score: float
    pdf_url: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    count: int
    latency_ms: float

class RAGRequest(BaseModel):
    query: str = Field(..., description="User query text", min_length=1)
    top_k: Optional[int] = Field(3, description="Number of context chunks", ge=1, le=10)
    temperature: Optional[float] = Field(0.0, description="LLM temperature", ge=0.0, le=1.0)

class RAGResponse(BaseModel):
    query: str
    answer: str
    sources: List[SearchResult]
    model_used: str
    search_latency_ms: float
    llm_latency_ms: float
    total_latency_ms: float

class HealthResponse(BaseModel):
    status: str
    milvus_connected: bool
    collection_exists: bool
    total_vectors: int
    embedding_model: str