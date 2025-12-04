import requests
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "deepseek/deepseek-chat"


def call_llm(system_msg: str, user_msg: str, temperature: float):
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is not set. "
            "Please set it to use the query enhancement feature."
        )
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        "temperature": temperature,
    }

    r = requests.post(BASE_URL, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def rewrite_query(original_query: str) -> str:
    system = (
        "You reformulate user queries for a Retrieval-Augmented Generation system. "
        "Make the query more specific and detailed for retrieval without changing the intent. "
        "Preserve the original language of the question."
    )
    user = f"Original query:\n{original_query}\n\nRewritten query:"
    return call_llm(system, user, temperature=0.3).strip()


def generate_hypothetical_document(query: str, target_chars: int = 1500) -> str:
    system = (
        "You write hypothetical long-form documents for a RAG system. "
        "The document is *only for retrieval*, not seen by the user. "
        "It should look like a detailed article answering the question."
    )
    user = (
        f"Question:\n{query}\n\n"
        f"Write a detailed document (~{target_chars} characters) that would plausibly answer it."
    )
    return call_llm(system, user, temperature=0.7).strip()


def enhance_query(original_query: str) -> dict:
    rewritten = rewrite_query(original_query)
    hypo = generate_hypothetical_document(rewritten)
    return {
        "original_query": original_query,
        "rewritten_query": rewritten,
        "hypothetical_document": hypo,
    }
