import json
import numpy as np
from pathlib import Path
from pymilvus import (
    connections, Collection, CollectionSchema, 
    FieldSchema, DataType, utility
)

def create_and_populate_collection():
    # Connect to Milvus
    connections.connect("default", host="localhost", port="19530")
    
    # Drop existing collection if exists
    if utility.has_collection("pdf_vectors"):
        utility.drop_collection("pdf_vectors")
        print("Dropped existing collection")
    
    # Define schema (1024 dim for bge-m3)
    fields = [
        FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=1024),
        FieldSchema("text", DataType.VARCHAR, max_length=5000),
        FieldSchema("source", DataType.VARCHAR, max_length=256),
        FieldSchema("page", DataType.INT64)
    ]
    
    schema = CollectionSchema(
        fields, 
        description="PDF chunks with BAAI/bge-m3 embeddings"
    )
    
    # Create collection
    collection = Collection("pdf_vectors", schema)
    print("✅ Collection 'pdf_vectors' created")
    
    # Load data
    embeddings = np.load("../processed/embeddings.npy")
    with open("../processed/final_chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} chunks and {embeddings.shape[0]} embeddings")
    
    # Prepare data for insertion
    insert_data = [
        embeddings.tolist(),
        [c["text"][:5000] for c in chunks],  # Truncate if needed
        [c["source"] for c in chunks],
        [c["page"] for c in chunks]
    ]
    
    # Insert
    print("Inserting data...")
    collection.insert(insert_data)
    collection.flush()
    print(f"✅ Inserted {collection.num_entities} vectors")
    
    # Create HNSW index with IP (dot product)
    print("Creating HNSW index...")
    index_params = {
        "metric_type": "IP",  # Inner Product (dot product)
        "index_type": "HNSW",
        "params": {
            "M": 16,
            "efConstruction": 200
        }
    }
    
    collection.create_index(
        field_name="embedding",
        index_params=index_params
    )
    print("✅ HNSW index created with IP metric")
    
    # Load collection
    collection.load()
    print("✅ Collection loaded into memory")
    
    return collection

if __name__ == "__main__":
    collection = create_and_populate_collection()
    print("\n🎉 Milvus setup complete!")