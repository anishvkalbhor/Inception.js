from backend.services.milvus_service import MilvusService
from backend.services.embedding_service import EmbeddingService
from backend.services.document_processor import DocumentProcessor
from backend.services.llm_service import LLMService

def get_milvus_service():
    return MilvusService()

def get_embedding_service():
    return EmbeddingService()

def get_document_processor():
    return DocumentProcessor()

def get_llm_service():
    return LLMService()