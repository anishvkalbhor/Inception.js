import httpx
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = os.getenv("LLM_MODEL")
        self.site_url = os.getenv("SITE_URL", "http://localhost:3000")  # Add to .env
        self.site_name = os.getenv("SITE_NAME", "VICTOR")  # Add to .env
        
    def create_prompt(self, query: str, contexts: List[Dict]) -> str:
        """Create RAG prompt with retrieved context"""
        
        # Build context string
        context_parts = []
        for i, ctx in enumerate(contexts, 1):
            context_parts.append(
                f"[Document {i}]\n"
                f"Source: {ctx['source']} (Page {ctx['page']})\n"
                f"Content: {ctx['text']}\n"
            )
        
        context_str = "\n---\n".join(context_parts)
        
        # Create prompt
        prompt = f"""You are a helpful assistant that answers questions based STRICTLY on the provided context.

Context Documents:
{context_str}

Instructions:
- You will construct the answer and present it with citations to the source documents.
- Answer the user's question using ONLY the information from the context above
- If the answer is not in the context, say "I cannot answer this question based on the provided documents"
- Always cite the source document and page number when answering
- Be accurate
- Do not add information that is not in the context
- Try to understand the language-style of the question and answer in the same language-style.

User Question: {query}

Answer:"""
        
        return prompt
    
    async def generate_answer(
        self, 
        query: str, 
        contexts: List[Dict], 
        temperature: float = 0.1
    ) -> str:
        """Generate answer using OpenRouter"""
        
        prompt = self.create_prompt(query, contexts)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            
            return answer

# Global instance
llm_client = None

def get_llm_client() -> OpenRouterClient:
    """Get or create OpenRouter client singleton"""
    global llm_client
    if llm_client is None:
        llm_client = OpenRouterClient()
    return llm_client