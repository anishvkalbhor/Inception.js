import subprocess
import os
import json

pdf_path = "PMSHRI.pdf"
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

print("Running FAST MinerU extraction (NO AI)...")

# Correct mineru command with -p flag
cmd = [
    "mineru",
    "-p", pdf_path,
    "-o", output_dir,
    "-m", "txt"  # Use text extraction method (fast, no OCR)
]

process = subprocess.run(cmd)

if process.returncode != 0:
    print("❌ MinerU extraction failed!")
    exit()

print("✅ MinerU fast extraction done!")
print(f"Output in: {output_dir}")

# -------------------------------------------------------------------
# Now load the JSON and merge blocks into paragraphs (FAST & CLEAN)
# -------------------------------------------------------------------

json_file = os.path.join(output_dir, "result.json")

if not os.path.exists(json_file):
    print("❌ ERROR: result.json not found. Check MinerU output.")
    exit()

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# MinerU FAST mode returns blocks like:
# [
#   { "text": "paragraph 1 ...", "bbox": [...] },
#   { "text": "paragraph 2 ...", "bbox": [...] },
# ]
# NO spans. NO tiny fragments. Already grouped.
# So we simply join them.

blocks = data.get("blocks") or data.get("elements") or data

paragraphs = []
for b in blocks:
    t = b.get("text", "").strip()
    if t:
        paragraphs.append(t)

clean_text = "\n\n".join(paragraphs)

# Save final merged text
text_out = os.path.join(output_dir, "clean_text.txt")
with open(text_out, "w", encoding="utf-8") as f:
    f.write(clean_text)

print("📝 Clean text saved to:", text_out)

# Images are already saved by MinerU in outputs/images/
print("🖼 Images extracted to:", os.path.join(output_dir, "images"))
