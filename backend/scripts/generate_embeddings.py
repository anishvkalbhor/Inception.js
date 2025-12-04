import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

def generate_embeddings(input_file="../processed/final_chunks.json"):
    # Load chunks
    with open(input_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} chunks")
    
    # Load model
    print("Loading BAAI/bge-m3 model...")
    model = SentenceTransformer('BAAI/bge-m3')
    
    # Extract texts
    texts = [chunk["text"] for chunk in chunks]
    
    # Generate embeddings (batch processing for efficiency)
    print("Generating embeddings...")
    embeddings = model.encode(
        texts,
        batch_size=8,  # Adjusted for 16GB RAM - increase if possible
        normalize_embeddings=True,  # Important for dot product
        show_progress_bar=True
    )
    
    # Save embeddings
    embeddings_path = Path("../processed/embeddings.npy")
    np.save(embeddings_path, embeddings)
    
    print(f"✅ Generated embeddings: shape {embeddings.shape}")
    print(f"✅ Saved to {embeddings_path}")
    
    # Verify dimension
    assert embeddings.shape[1] == 1024, f"Wrong dimension: {embeddings.shape[1]}"
    print(f"✅ Embedding dimension verified: 1024")
    
    return embeddings, chunks

if __name__ == "__main__":
    embeddings, chunks = generate_embeddings()