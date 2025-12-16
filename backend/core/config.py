from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings - HYBRID MODE (Online with Offline Fallback)"""

    # API
    APP_NAME: str = "VICTOR API (Hybrid Mode)"
    APP_VERSION: str = "2.0.0-hybrid"
    DEBUG: bool = True

    # MODE CONFIGURATION
    OFFLINE_MODE: bool = False  # Default to online (will auto-fallback)
    HYBRID_MODE: bool = True    # Enable automatic fallback
    PREFER_ONLINE: bool = True  # Try online first, fallback to offline

    # === ONLINE CONFIGURATION (Primary) ===
    
    # OpenRouter (Online LLM)
    OPENROUTER_API_KEY: str  = "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"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    ONLINE_LLM_MODEL: str = "alibaba/tongyi-deepresearch-30b-a3b:free"
    
    # ElevenLabs (Online Speech)
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
    
    # HuggingFace (Online Embeddings - fallback)
    HUGGINGFACE_API_KEY: Optional[str] = "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"
    ONLINE_EMBED_MODEL: str = "BAAI/bge-m3"

    # === OFFLINE CONFIGURATION (Fallback) ===
    
    # Ollama (Local LLM - Fallback)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "qwen2.5:3b"
    OLLAMA_EMBED_MODEL: str = "bge-m3"
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_MAX_TOKENS: int = 2000

    # === NETWORK & FALLBACK SETTINGS ===
    
    # Network check settings
    NETWORK_CHECK_TIMEOUT: int = 5  # seconds
    NETWORK_CHECK_URL: str = "https://api.openrouter.ai/api/v1/models"
    OLLAMA_CHECK_URL: str = "http://localhost:11434/api/tags"
    
    # Retry settings
    MAX_RETRIES: int = 2
    RETRY_DELAY: float = 1.0  # seconds
    
    # Cache settings
    CACHE_NETWORK_STATUS: int = 30  # seconds

    # === SHARED SETTINGS ===
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # Milvus
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    COLLECTION_NAME: str = "VictorText2"
    TOP_K: int = 5

    # MongoDB
    MONGODB_URI: str = "mongodb://admin:meow@localhost:27017/"
    MONGODB_DATABASE: str = "victor_rag"
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_USER: str = "admin"
    MONGO_PASSWORD: str = "meow"

    # Local storage
    LOCAL_STORAGE_ROOT: str = "data/local_storage"

    # Site Configuration
    SITE_URL: str = "http://localhost:3000"
    SITE_NAME: str = "VICTOR"

    # LLM Configuration (used by both modes)
    TEMPERATURE: float = 0.7
    MAX_NEW_TOKENS: int = 2000

    # Reranking
    ENABLE_RERANKING: bool = True
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RERANK_ALPHA: float = 0.5

    # Document processing
    CHUNK_SIZE: int = 1000

    # Security
    JWT_SECRET: str = "a69d50525ab6612f3ab1f418815f3bf3"

    # Google Drive (Online only)
    GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE: Optional[str] = None
    GOOGLE_DRIVE_MASTER_FOLDER_ID: Optional[str] = None
    GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON: Optional[str] = None

    # Cloudinary (Online only)
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Create a global settings instance
settings = get_settings()