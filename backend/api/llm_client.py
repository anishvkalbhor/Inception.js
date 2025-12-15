import httpx
import os
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
import logging
from typing import Optional, AsyncGenerator, List, Dict
from services.ollama_service import OllamaService
from services.network_monitor import get_network_monitor
from core.config import get_settings
import aiohttp

# Load .env from project root (parent of api folder)
env_path = Path(__file__).parent.parent / ".env"
print(f"🔍 Loading .env from: {env_path}")
print(f"✓ .env exists: {env_path.exists()}")

# Load the .env file
load_dotenv(env_path, override=True)

# Debug: print what's in the .env file
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if 'LLM_MODEL' in line:
                print(f"📄 Found in .env: {line.strip()}")

# Debug: check environment variable
llm_model_env = os.getenv("LLM_MODEL")
print(f"🔍 os.getenv('LLM_MODEL'): {llm_model_env}")

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = os.getenv("LLM_MODEL")
        self.site_url = os.getenv("SITE_URL", "http://localhost:3000")
        self.site_name = os.getenv("SITE_NAME", "VICTOR")
        
        # Set headers for OpenRouter API
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name
        }
        
        print(f"🚀 LLM Client Initialized with model: {self.model}")
        print(f"📍 OpenRouter Base URL: {self.base_url}")
        
    def create_prompt(self, query: str, contexts: List[Dict]) -> str:
        """Create enhanced RAG prompt with VictorText2 metadata"""
        if not contexts:
            context_str = "No relevant documents found."
        else:
            context_parts = []
            for i, ctx in enumerate(contexts, 1):
                context_desc = f"[Source {i}] Document: {ctx.get('document_name', 'Unknown')}"
                if ctx.get('page_idx'):
                    context_desc += f" (Page {ctx['page_idx']})"
                if ctx.get('ministry'):
                    context_desc += f" | Ministry: {ctx['ministry']}"
                if ctx.get('date'):
                    context_desc += f" | Date: {ctx['date']}"
                context_desc += f"\n{ctx.get('text', '')}"
                context_parts.append(context_desc)
            
            context_str = "\n\n---\n\n".join(context_parts)
        
        prompt = f"""You are VICTOR, a helpful, intelligent AI assistant specializing in government document analysis. Answer the user's question using the information found in the provided context from multiple documents.

CONTEXT:
{context_str}

INSTRUCTIONS:
- Use the context as your primary reference while applying deep analytical reasoning
- You may reason and make logical connections between information from different documents
- When reasoning across documents, clearly indicate your logical inference process
- Always cite document name, page number, and section when referencing information
- Include relevant metadata (ministry, date, document type) when it provides valuable context
- If the context doesn't contain sufficient information, state: "I cannot fully answer this question based on the provided documents."
- Explain naturally, clearly, and in a professional yet conversational tone
- Use step-by-step reasoning internally, but provide a cohesive, well-structured final answer

USER QUESTION:
{query}

ANSWER:"""
        return prompt

    async def generate_answer(
        self, 
        query: str, 
        contexts: List[Dict], 
        temperature: float = 0.1
    ) -> str:
        """Generate answer using OpenRouter with enhanced VictorText2 context"""
        if not contexts:
            context_text = "No relevant documents found."
        else:
            context_parts = []
            for i, ctx in enumerate(contexts, 1):
                context_desc = f"[Source {i}] Document: {ctx.get('document_name', 'Unknown')}"
                if ctx.get('page_idx'):
                    context_desc += f" (Page {ctx['page_idx']})"
                if ctx.get('ministry'):
                    context_desc += f" | Ministry: {ctx['ministry']}"
                if ctx.get('date'):
                    context_desc += f" | Date: {ctx['date']}"
                context_desc += f"\n{ctx.get('text', '')}"
                context_parts.append(context_desc)
            
            context_text = "\n\n---\n\n".join(context_parts)
            
            # Create the enhanced prompt
            prompt = f"""You are VICTOR, a helpful, intelligent AI assistant specializing in government document analysis. Answer the user's question using the information found in the provided context from multiple documents.

CONTEXT:
{context_text}

INSTRUCTIONS:
- Use the context as your primary reference while applying deep analytical reasoning
- You may reason and connect information across documents when logical
- Always cite document name, page number, and section/heading when referencing information
- Include relevant metadata (ministry, date, document type) when it adds valuable context
- If you cannot answer based on the provided documents, clearly state this
- Explain naturally, clearly, and in a professional yet conversational tone
- Connect information logically and provide meaningful insights
- Use step-by-step reasoning internally, but deliver a cohesive final answer

USER QUESTION:
{query}

ANSWER:"""

            print(f"📝 Enhanced prompt created with {len(contexts)} contexts")
            
            try:
                # Call OpenRouter API
                print(f"🔵 Calling OpenRouter API...")
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        self.base_url,
                        headers=self.headers,
                        json={
                            "model": self.model,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": temperature,
                            "max_tokens": 2500  # Increased for richer responses
                        }
                    )
                
                print(f"🔵 OpenRouter response status: {response.status_code}")
                
                if response.status_code != 200:
                    error_detail = response.text
                    print(f"❌ OpenRouter API Error ({response.status_code}): {error_detail}")
                    raise Exception(f"OpenRouter API Error ({response.status_code}): {error_detail}")
                
                result = response.json()
                print(f"🟢 Got enhanced result from OpenRouter")
                
                # Extract answer from response
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice:
                        answer = choice["message"]["content"]
                    elif "text" in choice:
                        answer = choice["text"]
                    else:
                        print(f"❌ Unexpected choice format: {choice.keys()}")
                        raise Exception(f"Unexpected response format: {result}")
                    
                    print(f"✅ Enhanced answer generated successfully")
                    return answer
                else:
                    print(f"❌ Unexpected OpenRouter response structure: {result}")
                    raise Exception(f"Unexpected response structure from OpenRouter: {result}")
            
            except Exception as e:
                print(f"❌ Error calling OpenRouter: {str(e)}")
                raise

class LLMClient:
    """LLM Client using local Ollama (offline)"""
    
    def __init__(self):
        self.settings = get_settings()
        self.ollama = OllamaService()
        
        # Check Ollama connection
        if not self.ollama.check_connection():
            raise ConnectionError(
                f"Cannot connect to Ollama. Make sure it's running: 'ollama serve'"
            )
        
        logger.info(f"🚀 LLM Client Initialized with OFFLINE model: {self.settings.OLLAMA_LLM_MODEL}")
        logger.info(f"📍 Ollama URL: {self.settings.OLLAMA_BASE_URL}")
    
    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate response using local Ollama"""
        return await self.ollama.generate_response(
            prompt=prompt,
            context=context,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None
    ) -> AsyncGenerator[str, None]:
        """Stream responses using local Ollama"""
        async for chunk in self.ollama.chat_stream(messages, temperature=temperature):
            yield chunk
    
    def is_offline(self) -> bool:
        """Check if running in offline mode"""
        return True  # Always offline with Ollama

# Global instance
llm_client = None

def get_llm_client() -> OpenRouterClient:
    """Get or create OpenRouter client singleton"""
    global llm_client
    if llm_client is None:
        llm_client = OpenRouterClient()
    return llm_client

class HybridLLMClient:
    """
    Hybrid LLM Client with automatic fallback
    Tries online (OpenRouter) first, falls back to offline (Ollama)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.ollama = OllamaService()
        self.network_monitor = get_network_monitor()
        self._current_mode: Optional[str] = None
        
        logger.info("🔄 Hybrid LLM Client initialized")
        logger.info(f"   Primary: {'Online' if self.settings.PREFER_ONLINE else 'Offline'}")
        logger.info(f"   Online Model: {self.settings.ONLINE_LLM_MODEL}")
        logger.info(f"   Offline Model: {self.settings.OLLAMA_LLM_MODEL}")
    
    async def _detect_mode(self) -> str:
        """Detect and cache current mode"""
        if not self._current_mode:
            self._current_mode = await self.network_monitor.get_best_mode()
        return self._current_mode
    
    def reset_mode(self):
        """Force mode re-detection on next call"""
        self._current_mode = None
        self.network_monitor.invalidate_cache()
    
    async def _generate_online(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate using online API (OpenRouter)"""
        if not self.settings.OPENROUTER_API_KEY:
            raise ValueError("OpenRouter API key not configured")
        
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        
        messages.append({"role": "user", "content": prompt})
        
        # API request
        url = f"{self.settings.OPENROUTER_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": self.settings.SITE_URL,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.settings.ONLINE_LLM_MODEL,
            "messages": messages,
            "temperature": temperature or self.settings.TEMPERATURE,
            "max_tokens": max_tokens or self.settings.MAX_NEW_TOKENS
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API error: {response.status} - {error_text}")
                
                data = await response.json()
                return data["choices"][0]["message"]["content"]
    
    async def _generate_offline(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate using offline (Ollama)"""
        return await self.ollama.generate_response(
            prompt=prompt,
            context=context,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
        force_mode: Optional[str] = None
    ) -> str:
        """
        Generate response with automatic fallback
        
        Args:
            force_mode: Override auto-detection ('online' or 'offline')
        """
        # Determine mode
        if force_mode:
            mode = force_mode
        else:
            mode = await self._detect_mode()
        
        # Try primary mode
        try:
            if mode == "online":
                logger.info("🌐 Using online LLM (OpenRouter)")
                return await self._generate_online(
                    prompt, context, system_prompt, temperature, max_tokens
                )
            elif mode == "offline":
                logger.info("⚡ Using offline LLM (Ollama)")
                return await self._generate_offline(
                    prompt, context, system_prompt, temperature, max_tokens
                )
            else:
                raise Exception("No LLM services available")
        
        except Exception as e:
            logger.warning(f"⚠️  Primary mode ({mode}) failed: {e}")
            
            # Try fallback
            if mode == "online":
                logger.info("🔄 Falling back to offline (Ollama)...")
                try:
                    return await self._generate_offline(
                        prompt, context, system_prompt, temperature, max_tokens
                    )
                except Exception as fallback_error:
                    logger.error(f"❌ Offline fallback also failed: {fallback_error}")
                    raise Exception(f"Both online and offline LLM failed. Last error: {fallback_error}")
            
            elif mode == "offline":
                logger.info("🔄 Falling back to online (OpenRouter)...")
                try:
                    return await self._generate_online(
                        prompt, context, system_prompt, temperature, max_tokens
                    )
                except Exception as fallback_error:
                    logger.error(f"❌ Online fallback also failed: {fallback_error}")
                    raise Exception(f"Both offline and online LLM failed. Last error: {fallback_error}")
            
            raise
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None
    ) -> AsyncGenerator[str, None]:
        """Stream responses (currently offline only)"""
        mode = await self._detect_mode()
        
        if mode == "offline":
            async for chunk in self.ollama.chat_stream(messages, temperature):
                yield chunk
        else:
            # TODO: Implement online streaming
            response = await self.generate(
                prompt=messages[-1]["content"],
                temperature=temperature
            )
            yield response
    
    def get_current_mode(self) -> Optional[str]:
        """Get current mode without checking"""
        return self._current_mode
    
    async def get_status(self) -> Dict:
        """Get detailed status of all services"""
        online_ok, ollama_ok = await self.network_monitor.check_services(use_cache=False)
        mode = await self._detect_mode()
        
        return {
            "current_mode": mode,
            "services": {
                "online": {
                    "available": online_ok,
                    "model": self.settings.ONLINE_LLM_MODEL,
                    "api_key_configured": bool(self.settings.OPENROUTER_API_KEY)
                },
                "offline": {
                    "available": ollama_ok,
                    "model": self.settings.OLLAMA_LLM_MODEL,
                    "url": self.settings.OLLAMA_BASE_URL
                }
            },
            "prefer_online": self.settings.PREFER_ONLINE,
            "hybrid_mode": self.settings.HYBRID_MODE
        }


# Alias for backwards compatibility
LLMClient = HybridLLMClient