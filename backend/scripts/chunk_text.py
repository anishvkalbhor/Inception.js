import json
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

def chunk_text(input_file="../processed/raw_chunks.json"):
    # Load raw chunks
    with open(input_file, "r", encoding="utf-8") as f:
        raw_chunks = json.load(f)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len
    )
    
    final_chunks = []
    for item in tqdm(raw_chunks, desc="Chunking text"):
        splits = splitter.split_text(item["text"])
        for i, split in enumerate(splits):
            final_chunks.append({
                "text": split,
                "source": item["source"],
                "page": item["page"],
                "chunk_id": i
            })
    
    # Save
    output_path = Path("../processed/final_chunks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created {len(final_chunks)} chunks")
    print(f"✅ Saved to {output_path}")
    return final_chunks

if __name__ == "__main__":
    chunks = chunk_text()
    print(f"\nSample chunk:\n{chunks[0]}")