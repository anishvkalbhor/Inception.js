import subprocess
import json
import os

pdf_path = "NEP.pdf"
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

try:
    # Use mineru command line tool to parse PDF
    print(f"Parsing {pdf_path} with MinerU...")
    print("This may take a few minutes...\n")
    
    result = subprocess.run(
        ["mineru", "-p", pdf_path, "-o", output_dir],
        capture_output=False,  # Show output in real-time
        text=True
    )
    
    if result.returncode == 0:
        print("\n✅ PDF parsed successfully!")
        print(f"Output saved to {output_dir}")
        
        # List generated files
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            print(f"\nGenerated files ({len(files)}):")
            for f in files:
                print(f"  - {f}")
    else:
        print(f"\n❌ Error occurred (exit code: {result.returncode})")
    
except FileNotFoundError:
    print("❌ mineru command not found")
    print("Try installing: pip install mineru")
    print("Or use: mineru extract NEP.pdf -o outputs")
    
except Exception as e:
    print(f"❌ Error: {e}")
