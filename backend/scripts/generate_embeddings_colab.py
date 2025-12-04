"""
Google Colab GPU-Optimized Embedding Generation Script
For BAAI/bge-m3 model on T4 GPU

Instructions:
1. Upload this script to Colab
2. Upload your final_chunks.json file
3. Set Runtime -> Change runtime type -> T4 GPU
4. Run all cells
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import torch

def generate_embeddings_gpu(input_file="final_chunks.json"):
    """
    Generate embeddings using GPU acceleration
    Optimized for Google Colab T4 GPU
    """
    # Check GPU availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔥 Using device: {device}")
    
    if device == "cuda":
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    # Load chunks
    print(f"\n📁 Loading chunks from {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    print(f"✅ Loaded {len(chunks)} chunks")
    
    # Load model on GPU
    print("\n🤖 Loading BAAI/bge-m3 model on GPU...")
    model = SentenceTransformer('BAAI/bge-m3', device=device)
    
    # Model info
    print(f"✅ Model loaded: BAAI/bge-m3")
    print(f"   Embedding dimension: 1024")
    print(f"   Max sequence length: {model.max_seq_length}")
    
    # Extract texts
    texts = [chunk["text"] for chunk in chunks]
    
    # Generate embeddings with GPU optimization
    print("\n⚡ Generating embeddings on GPU...")
    print("   (This will be MUCH faster than CPU!)")
    
    embeddings = model.encode(
        texts,
        batch_size=128,  # T4 GPU can handle large batches (16GB VRAM)
        normalize_embeddings=True,  # Important for dot product similarity
        show_progress_bar=True,
        device=device,
        convert_to_numpy=True  # Convert to numpy for saving
    )
    
    # Save embeddings
    embeddings_path = "embeddings.npy"
    np.save(embeddings_path, embeddings)
    
    print(f"\n✅ Generated embeddings: shape {embeddings.shape}")
    print(f"✅ Saved to {embeddings_path}")
    
    # Verify dimension
    assert embeddings.shape[1] == 1024, f"Wrong dimension: {embeddings.shape[1]}"
    print(f"✅ Embedding dimension verified: 1024")
    
    # Memory cleanup
    if device == "cuda":
        torch.cuda.empty_cache()
        print(f"✅ GPU memory cleared")
    
    return embeddings, chunks


def main():
    """
    Main execution for Colab
    """
    print("="*60)
    print("🚀 BAAI/bge-m3 Embedding Generation (GPU-Optimized)")
    print("="*60)
    
    # Generate embeddings
    embeddings, chunks = generate_embeddings_gpu()
    
    # Print statistics
    print("\n" + "="*60)
    print("📊 STATISTICS")
    print("="*60)
    print(f"Total chunks processed: {len(chunks)}")
    print(f"Embedding shape: {embeddings.shape}")
    print(f"Embedding size: {embeddings.nbytes / 1e6:.2f} MB")
    print(f"Average embedding norm: {np.linalg.norm(embeddings, axis=1).mean():.4f}")
    
    # Sample output
    print("\n📝 Sample chunk:")
    print(f"Source: {chunks[0]['source']}")
    print(f"Page: {chunks[0]['page']}")
    print(f"Chunk ID: {chunks[0]['chunk_id']}")
    print(f"Text preview: {chunks[0]['text'][:200]}...")
    
    print("\n✅ Done! Download 'embeddings.npy' from Colab files.")
    print("="*60)


if __name__ == "__main__":
    main()


# ============================================================
# COLAB NOTEBOOK CELLS (Copy these to separate cells in Colab)
# ============================================================

"""
CELL 1: Install Dependencies
----------------------------
!pip install -q sentence-transformers torch numpy


CELL 2: Upload Files
-------------------
from google.colab import files
print("📤 Upload your final_chunks.json file:")
uploaded = files.upload()


CELL 3: Run Embedding Generation
--------------------------------
!python generate_embeddings_colab.py


CELL 4: Download Results
-----------------------
from google.colab import files
print("📥 Downloading embeddings.npy...")
files.download('embeddings.npy')


ALTERNATIVE: Run directly in notebook (recommended)
--------------------------------------------------
# Just copy the generate_embeddings_gpu() function above and run:

import json
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from tqdm import tqdm

# Upload file
from google.colab import files
uploaded = files.upload()

# Generate embeddings
embeddings, chunks = generate_embeddings_gpu("final_chunks.json")

# Download results
from google.colab import files
files.download('embeddings.npy')
"""
