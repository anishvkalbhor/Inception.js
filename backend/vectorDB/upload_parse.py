# backend/vectorDB/upload_parse.py

import subprocess
import os
from pathlib import Path
import sys
import json
from datetime import datetime

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def is_already_parsed(output_dir: Path) -> bool:
    """
    Check if MinerU output already exists.
    """
    marker_files = [
        output_dir / "auto" / "content_list.json",
        output_dir / "auto" / "layout.pdf",
        output_dir / "auto" / "middle.json",
    ]
    return any(p.exists() for p in marker_files)


def parse_single_pdf(pdf_path: Path, output_dir: Path, skip_existing: bool = True):
    """
    Parse ONE PDF using MinerU (upload pipeline safe).
    """
    if skip_existing and is_already_parsed(output_dir):
        print(f"⏭️  Skipping already parsed PDF: {pdf_path.name}")
        return "skipped"

    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print(f"📄 Parsing PDF (upload pipeline)")
    print(f"PDF: {pdf_path}")
    print(f"Output: {output_dir}")
    print("=" * 60)

    try:
        result = subprocess.run(
            ["mineru", "-p", str(pdf_path), "-o", str(output_dir)],
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8',  
            errors='replace'
        )

        if result.returncode == 0:
            print(f"✅ Successfully parsed: {pdf_path.name}")
            # Add metadata preservation
            metadata = {
                "filename": pdf_path.stem,
                "parsed_date": datetime.now().isoformat()
            }
            # Save metadata to JSON
            output_data = {
                "metadata": metadata
            }
            json_output = output_dir / f"{pdf_path.stem}_metadata.json"
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
            print(f"✅ Metadata saved: {json_output}")
            return "success"
        else:
            print(f"❌ MinerU failed (exit code {result.returncode})")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return "failed"

    except FileNotFoundError:
        print("❌ mineru command not found")
        print("Install with: pip install magic-pdf[full]")
        return "error"
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return "error"


def main():
    """
    Entry point for upload pipeline parsing.
    Assumes:
      - Script is called with cwd set to upload version directory
      - original.pdf exists in that directory
    """
    base_dir = Path(os.getcwd())
    
    print(f"🔍 Working directory: {base_dir}")
    print(f"🔍 Directory contents: {list(base_dir.iterdir())}")
    
    pdf_path = base_dir / "original.pdf"
    output_dir = base_dir / "outputs"

    if not pdf_path.exists():
        print(f"❌ original.pdf not found in {base_dir}")
        print(f"   Expected: {pdf_path}")
        sys.exit(1)

    print(f"✅ Found PDF: {pdf_path}")
    result = parse_single_pdf(pdf_path, output_dir, skip_existing=True)

    if result not in {"success", "skipped"}:
        sys.exit(2)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
