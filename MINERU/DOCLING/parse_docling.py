import os
from docling.document_converter import DocumentConverter

def parse_with_docling(input_file):
    # Create converter
    converter = DocumentConverter()

    # Convert the file
    result = converter.convert(input_file)

    # Output folder for parsed result
    base = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = f"parsed/{base}"
    os.makedirs(output_dir, exist_ok=True)

    # Save markdown
    md_path = os.path.join(output_dir, "output.md")
    result.document.save_as_markdown(md_path)

    # Save structured JSON
    json_path = os.path.join(output_dir, "output.json")
    result.document.save_as_json(json_path)

    print("✔ Markdown saved to:", md_path)
    print("✔ JSON saved to:", json_path)

    return {
        "markdown": md_path,
        "json": json_path,
        "output_dir": output_dir
    }

if __name__ == "__main__":
    file_path = input("Enter file path: ")
    parse_with_docling(file_path)
