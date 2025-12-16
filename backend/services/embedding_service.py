import logging
from typing import List, Optional, Dict
from services.ollama_service import OllamaService
from services.network_monitor import get_network_monitor
from core.config import get_settings
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class HybridEmbeddingService:
    """
    Hybrid Embedding Service with automatic fallback
    Tries online (HuggingFace) first, falls back to offline (Ollama)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.ollama = OllamaService()
        self.network_monitor = get_network_monitor()
        self._current_mode: Optional[str] = None
        
        logger.info("🔄 Hybrid Embedding Service initialized")
    
    async def _detect_mode(self) -> str:
        """Detect best mode for embeddings"""
        if not self._current_mode:
            self._current_mode = await self.network_monitor.get_best_mode()
        return self._current_mode
    
    async def _create_embeddings_online(
        self,
        texts: List[str],
        batch_size: int = 20
    ) -> List[List[float]]:
        """Create embeddings using OpenRouter API (online)"""
        import os
        import aiohttp

        api_key = self.settings.OPENROUTER_API_KEY
        if not api_key:
            raise ValueError("OpenRouter API key not configured")
        url = "https://openrouter.ai/api/v1/embeddings"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"input": texts, "model": "baai/bge-m3"}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"OpenRouter API error: {resp.status}")
                data = await resp.json()
                return data["embeddings"]

    async def _create_embeddings_offline(
        self,
        texts: List[str],
        batch_size: int = 20
    ) -> List[List[float]]:
        """Create embeddings using Ollama (offline)"""
        return await self.ollama.generate_embeddings(texts, batch_size)
    
    async def create_embeddings(
        self,
        texts: List[str],
        batch_size: int = 20,
        force_mode: Optional[str] = None
    ) -> List[List[float]]:
        """
        Create embeddings with automatic fallback

        Args:
            force_mode: Override auto-detection ('online' or 'offline')
        """
        mode = force_mode or await self._detect_mode()

        if mode == "online":
            try:
                logger.info(f"⚡ Creating embeddings using OpenRouter (online)")
                return await self._create_embeddings_online(texts, batch_size)
            except Exception as e:
                logger.warning(f"Online embedding failed, falling back to Ollama: {e}")

        # Fallback to offline
        logger.info(f"⚡ Creating embeddings using Ollama (offline)")
        return await self._create_embeddings_offline(texts, batch_size)
    
    async def create_single_embedding(
        self,
        text: str,
        force_mode: Optional[str] = None
    ) -> List[float]:
        """Create embedding for a single text"""
        embeddings = await self.create_embeddings([text], force_mode=force_mode)
        return embeddings[0]
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension (bge-m3 = 1024)"""
        return 1024
    
    async def get_status(self) -> Dict:
        """Get status of embedding services"""
        mode = await self._detect_mode()
        ollama_ok = await self.network_monitor.check_ollama()
        
        return {
            "current_mode": mode,
            "offline_available": ollama_ok,
            "offline_model": self.settings.OLLAMA_EMBED_MODEL,
            "dimension": self.get_embedding_dimension()
        }


# Alias for backwards compatibility
EmbeddingService = HybridEmbeddingService