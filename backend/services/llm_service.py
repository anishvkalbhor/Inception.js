import logging
from typing import List, Dict, Optional, AsyncGenerator
from services.ollama_service import OllamaService
from core.config import get_settings

logger = logging.getLogger(__name__)

class LLMService:
    """LLM Service using local Ollama (qwen2.5:3b)"""
    
    def __init__(self):
        self.ollama = OllamaService()
        self.settings = get_settings()
        logger.info(f"Initialized LLMService with Ollama model: {self.settings.OLLAMA_LLM_MODEL}")
    
    async def generate_answer(
        self,
        query: str,
        context: str = None,
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate answer using local Ollama"""
        try:
            system_prompt = """You are VICTOR, a helpful AI assistant specialized in answering questions based on provided context.
Always provide accurate, relevant answers based on the context given.
If the context doesn't contain relevant information, say so clearly."""
            
            # Add conversation history to messages if provided
            if conversation_history:
                # Build messages with history
                messages = [{"role": "system", "content": system_prompt}]
                
                for msg in conversation_history[-5:]:  # Last 5 messages
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
                
                # Add current query with context
                user_message = f"Context:\n{context}\n\nQuestion: {query}" if context else query
                messages.append({"role": "user", "content": user_message})
                
                # Use chat method for conversation
                response = ""
                async for chunk in self.ollama.chat_stream(messages, temperature=temperature):
                    response += chunk
                return response
            else:
                # Single turn question answering
                return await self.ollama.generate_response(
                    prompt=query,
                    context=context,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    async def stream_answer(
        self,
        query: str,
        context: str = None,
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = None
    ) -> AsyncGenerator[str, None]:
        """Stream answer using local Ollama"""
        try:
            system_prompt = """You are VICTOR, a helpful AI assistant specialized in answering questions based on provided context.
Always provide accurate, relevant answers based on the context given.
If the context doesn't contain relevant information, say so clearly."""
            
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-5:]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Add current query with context
            user_message = f"Context:\n{context}\n\nQuestion: {query}" if context else query
            messages.append({"role": "user", "content": user_message})
            
            # Stream response
            async for chunk in self.ollama.chat_stream(messages, temperature=temperature):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error streaming answer: {e}")
            raise