import PyPDF2
import json
from pathlib import Path
from tqdm import tqdm

def extract_text_from_pdfs(pdf_dir="../data"):
    chunks = []
    pdf_files = list(Path(pdf_dir).glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files")
    
    for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        chunks.append({
                            "text": text.strip(),
                            "source": pdf_path.name,
                            "page": page_num + 1
                        })
        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")
    
    # Save to processed/
    output_path = Path("../processed/raw_chunks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Extracted {len(chunks)} pages")
    print(f"✅ Saved to {output_path}")
    return chunks

if __name__ == "__main__":
    chunks = extract_text_from_pdfs()