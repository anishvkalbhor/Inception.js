from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from backend.services.milvus_service import MilvusService
from backend.services.embedding_service import EmbeddingService
from backend.services.document_processor import DocumentProcessor
from backend.api.dependencies import get_milvus_service, get_embedding_service, get_document_processor

router = APIRouter()

@router.post("/upload")
async def upload_document(
    collection_name: str = Form(...),
    file: UploadFile = File(...),
    milvus: MilvusService = Depends(get_milvus_service),
    embedding: EmbeddingService = Depends(get_embedding_service),
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """Upload and process PDF document"""
    try:
        # Read file
        file_bytes = await file.read()
        
        # Process PDF
        chunks = processor.process_pdf(file_bytes)
        
        # Generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding.embed_batch(texts)
        
        # Prepare metadata
        metadata = [
            {
                "document_id": file.filename,
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "page_number": chunk["page_number"]
            }
            for chunk in chunks
        ]
        
        # Insert into Milvus
        milvus.insert_vectors(
            collection_name=collection_name,
            embeddings=embeddings,
            metadata=metadata
        )
        
        return {
            "filename": file.filename,
            "chunks": len(chunks),
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))