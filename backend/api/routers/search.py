from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
import json
from pathlib import Path
from typing import List, Optional

# Import MongoDB service
from services.mongodb_service import find_documents
router = APIRouter()

class SearchRequest(BaseModel):
    collection_name: str
    query: str
    top_k: int = 5

class QueryRequest(BaseModel):
    query: str
    top_k: int = 10

class SearchResult(BaseModel):
    id: str
    text: str
    score: float

@router.post("/")
async def search(request: SearchRequest):
    """Search within a collection"""
    # Basic demo search without Milvus
    return {
        "query": request.query,
        "collection": request.collection_name,
        "results": [
            {"id": "1", "text": "Demo result 1", "score": 0.95},
            {"id": "2", "text": "Demo result 2", "score": 0.87}
        ]
    }

@router.post("/query")
async def search_query(request: QueryRequest):
    """
    Search across all documents using simple text matching.
    Returns top_k documents with excerpts matching the query.
    """
    try:
        query_lower = request.query.lower()
        
        # Get all documents from MongoDB
        documents = await asyncio.to_thread(find_documents, {})
        
        if not documents:
            return {
                "query": request.query,
                "results": []
            }
        
        # Simple text matching scoring
        scored_results = []
        
        for doc in documents:
            if not doc.get("filename"):
                continue
            
            score = 0.0
            excerpt = ""
            
            # Try to read parsed.json for full text search
            try:
                parsed_path = doc.get("parsed_json_local_path")
                if parsed_path and Path(parsed_path).exists():
                    with open(parsed_path, "r", encoding="utf-8") as f:
                        parsed_data = json.load(f)
                        full_text = parsed_data.get("full_text_preview", "")
                        
                        # Simple keyword matching score
                        if full_text:
                            text_lower = full_text.lower()
                            # Count keyword occurrences
                            occurrences = text_lower.count(query_lower)
                            if occurrences > 0:
                                # Score based on occurrences (max 0.5) + presence bonus (0.5)
                                score = min(0.5, occurrences * 0.1) + 0.5
                                
                                # Extract excerpt around first match
                                pos = text_lower.find(query_lower)
                                if pos != -1:
                                    start = max(0, pos - 100)
                                    end = min(len(full_text), pos + len(query_lower) + 100)
                                    excerpt = full_text[start:end].strip()
                                    if start > 0:
                                        excerpt = "..." + excerpt
                                    if end < len(full_text):
                                        excerpt = excerpt + "..."
            except Exception as e:
                print(f"Error reading parsed.json for {doc.get('filename')}: {e}")
                continue
            
            if score > 0:
                scored_results.append({
                    "id": str(doc.get("_id", "")),
                    "filename": doc.get("filename", "Unknown"),
                    "excerpt": excerpt or "No preview available",
                    "score": score,
                    "local_path": doc.get("local_path", ""),
                })
        
        # Sort by score descending and limit to top_k
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        top_results = scored_results[:request.top_k]
        
        return {
            "query": request.query,
            "results": top_results
        }
        
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")