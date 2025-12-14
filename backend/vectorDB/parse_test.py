import subprocess
import json
import os
from pathlib import Path

# Source directory containing PDFs
source_dir = "../data/local_storage"
output_base_dir = "outputs"

def find_all_pdfs(directory):
    """Recursively find all PDF files in directory and subdirectories"""
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return sorted(pdf_files)  # Sort for consistent ordering

def is_already_parsed(pdf_path, output_dir):
    """Check if PDF has already been parsed by looking for output files"""
    # Check for common MinerU output files
    marker_files = [
        "auto/content_list.json",
        "auto/layout.pdf",
        "auto/middle.json"
    ]
    
    for marker in marker_files:
        marker_path = os.path.join(output_dir, marker)
        if os.path.exists(marker_path):
            return True
    return False

def parse_pdf(pdf_path, output_dir, skip_existing=True):
    """Parse a single PDF using MinerU"""
    
    # Check if already parsed
    if skip_existing and is_already_parsed(pdf_path, output_dir):
        print(f"⏭️  Skipping (already parsed): {os.path.basename(pdf_path)}")
        return "skipped"
    
    try:
        print(f"\n{'='*60}")
        print(f"Parsing: {pdf_path}")
        print(f"Output to: {output_dir}")
        print('='*60)
        
        result = subprocess.run(
            ["mineru", "-p", pdf_path, "-o", output_dir],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Successfully parsed: {os.path.basename(pdf_path)}")
            return "success"
        else:
            print(f"❌ Failed to parse: {os.path.basename(pdf_path)} (exit code: {result.returncode})")
            return "failed"
            
    except Exception as e:
        print(f"❌ Error parsing {os.path.basename(pdf_path)}: {e}")
        return "error"

def find_resume_point(pdf_files, last_parsed_pdf="Clarification13042016.pdf"):
    """Find where to resume parsing from"""
    try:
        # Find index of last parsed PDF
        for i, pdf_path in enumerate(pdf_files):
            if last_parsed_pdf in os.path.basename(pdf_path):
                print(f"📍 Found resume point: {os.path.basename(pdf_path)}")
                print(f"   Position: {i+1}/{len(pdf_files)}")
                return i + 1  # Start from next PDF
        
        print(f"⚠️ Could not find '{last_parsed_pdf}' in PDF list")
        return 0  # Start from beginning
    except Exception as e:
        print(f"⚠️ Error finding resume point: {e}")
        return 0

def main():
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"❌ Source directory not found: {source_dir}")
        return
    
    # Find all PDFs
    print(f"Searching for PDFs in: {source_dir}")
    pdf_files = find_all_pdfs(source_dir)
    
    if not pdf_files:
        print(f"❌ No PDF files found in {source_dir}")
        return
    
    print(f"\n📚 Found {len(pdf_files)} PDF file(s)")
    
    # Create base output directory
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Check for already parsed PDFs
    print(f"\n🔍 Checking for already parsed PDFs...")
    already_parsed = []
    to_parse = []
    
    for pdf_path in pdf_files:
        # Create unique output directory for each PDF
        rel_path = os.path.relpath(pdf_path, source_dir)
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = os.path.join(output_base_dir, os.path.dirname(rel_path), pdf_name)
        
        if is_already_parsed(pdf_path, output_dir):
            already_parsed.append(pdf_path)
        else:
            to_parse.append(pdf_path)
    
    print(f"\n📊 Status:")
    print(f"   ✅ Already parsed: {len(already_parsed)}")
    print(f"   📝 To parse: {len(to_parse)}")
    
    if not to_parse:
        print(f"\n✅ All PDFs have already been parsed!")
        return
    
    # Show first few PDFs to parse
    print(f"\n📋 Next PDFs to parse:")
    for pdf in to_parse[:5]:
        print(f"   - {os.path.basename(pdf)}")
    if len(to_parse) > 5:
        print(f"   ... and {len(to_parse) - 5} more")
    
    # Ask for confirmation
    response = input(f"\n❓ Continue parsing {len(to_parse)} remaining PDFs? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Parsing cancelled")
        return
    
    # Process each PDF
    successful = 0
    failed = 0
    skipped = len(already_parsed)
    
    for i, pdf_path in enumerate(to_parse, 1):
        print(f"\n📄 Processing {i}/{len(to_parse)}: {os.path.basename(pdf_path)}")
        
        # Create unique output directory for each PDF
        rel_path = os.path.relpath(pdf_path, source_dir)
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = os.path.join(output_base_dir, os.path.dirname(rel_path), pdf_name)
        os.makedirs(output_dir, exist_ok=True)
        
        result = parse_pdf(pdf_path, output_dir, skip_existing=True)
        
        if result == "success":
            successful += 1
        elif result == "skipped":
            skipped += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 FINAL SUMMARY")
    print('='*60)
    print(f"Total PDFs: {len(pdf_files)}")
    print(f"⏭️  Already parsed (skipped): {skipped}")
    print(f"✅ Newly parsed: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"Output directory: {output_base_dir}")

if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        print("❌ mineru command not found")
        print("Try installing: pip install mineru")
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")