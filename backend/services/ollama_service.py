import ollama
from typing import List, Dict, Optional, AsyncGenerator
import logging
from core.config import get_settings
import asyncio

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(
        self, 
        model: str = None,
        embed_model: str = None,
        base_url: str = None
    ):
        settings = get_settings()
        self.model = model or settings.OLLAMA_LLM_MODEL
        self.embed_model = embed_model or settings.OLLAMA_EMBED_MODEL
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        
        try:
            self.client = ollama.Client(host=self.base_url)
            logger.info(f"Initialized Ollama client: {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            raise
    
    def check_connection(self) -> bool:
        """Verify Ollama is running and models are available"""
        try:
            # Try to list models
            models_response = self.client.list()
            
            # Handle different response formats
            if isinstance(models_response, dict):
                models_list = models_response.get('models', [])
            else:
                models_list = models_response
            
            # Extract model names
            available_models = []
            for m in models_list:
                if isinstance(m, dict):
                    # Try different possible keys
                    model_name = m.get('name') or m.get('model') or m.get('id')
                    if model_name:
                        available_models.append(model_name)
                else:
                    available_models.append(str(m))
            
            logger.info(f"Available models: {available_models}")
            
            # Check if required models are available
            model_found = any(self.model in m for m in available_models)
            embed_found = any(self.embed_model in m for m in available_models)
            
            if not model_found:
                logger.error(f"Model {self.model} not found in: {available_models}")
                return False
            
            if not embed_found:
                logger.error(f"Embedding model {self.embed_model} not found in: {available_models}")
                return False
            
            logger.info(f"✅ Using LLM: {self.model}, Embeddings: {self.embed_model}")
            return True
            
        except ConnectionError as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            logger.error("Make sure Ollama is running: 'ollama serve'")
            return False
        except Exception as e:
            logger.error(f"Ollama connection check failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate response using Qwen 2.5:3b"""
        try:
            settings = get_settings()
            messages = []
            
            # Add system prompt
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Construct user message with context
            user_content = prompt
            if context:
                user_content = f"""Context information:
{context}

Based on the above context, please answer the following question:
{prompt}

If the context doesn't contain relevant information, please say so."""
            
            messages.append({
                "role": "user",
                "content": user_content
            })
            
            # Generate response
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.model,
                messages=messages,
                options={
                    'temperature': temperature or settings.OLLAMA_TEMPERATURE,
                    'num_predict': max_tokens or settings.OLLAMA_MAX_TOKENS,
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
    
    async def chat_stream(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        temperature: float = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses"""
        try:
            settings = get_settings()
            
            # Add system prompt if not present
            if system_prompt and (not messages or messages[0].get("role") != "system"):
                messages.insert(0, {
                    "role": "system",
                    "content": system_prompt
                })
            
            # Stream in thread to not block
            def _stream():
                return self.client.chat(
                    model=self.model,
                    messages=messages,
                    stream=True,
                    options={
                        'temperature': temperature or settings.OLLAMA_TEMPERATURE
                    }
                )
            
            stream = await asyncio.to_thread(_stream)
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    if content:
                        yield content
                        
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise
    
    async def generate_embeddings(
        self, 
        texts: List[str],
        batch_size: int = 20
    ) -> List[List[float]]:
        """Generate embeddings using nomic-embed-text"""
        try:
            embeddings = []
            total_batches = (len(texts) + batch_size - 1) // batch_size
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                logger.info(f"Processing embedding batch {batch_num}/{total_batches}")
                
                for text in batch:
                    # Generate embedding in thread
                    response = await asyncio.to_thread(
                        self.client.embeddings,
                        model=self.embed_model,
                        prompt=text
                    )
                    embeddings.append(response['embedding'])
            
            logger.info(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            raise
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        try:
            return {
                "llm_model": self.model,
                "embed_model": self.embed_model,
                "base_url": self.base_url,
                "status": "connected" if self.check_connection() else "disconnected"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }