"""
Process parsed MinerU PDFs with improved OCR correction, then chunk into semantic paragraphs.
Prepares data for embedding generation with proper unique identifiers.
"""

import json
import os
import re
import sys
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from pymongo import MongoClient
import hashlib
import uuid

# ✅ ADDED: Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class OCRTextCleaner:
    """Clean and fix OCR errors in parsed text with improved regex patterns"""
    
    def __init__(self):
        pass
    
    def fix_spaced_words(self, text: str) -> str:
        """
        Fix words with excessive spaces like 'u n i ve rs i ty' -> 'university'
        Uses multiple passes to catch nested patterns
        """
        # Pattern 1: Single letters with single spaces (most common)
        # Matches: "u n i v e r s i t y"
        pattern1 = r'\b([a-z])\s+([a-z])\s+([a-z])'
        for _ in range(10):  # Multiple passes
            prev_text = text
            text = re.sub(pattern1, r'\1\2\3', text, flags=re.IGNORECASE)
            if prev_text == text:  # No more changes
                break
        
        # Pattern 2: Single letters with multiple spaces
        # Matches: "u  n  i  v"
        pattern2 = r'\b([a-z])\s{2,}([a-z])'
        for _ in range(5):
            prev_text = text
            text = re.sub(pattern2, r'\1\2', text, flags=re.IGNORECASE)
            if prev_text == text:
                break
        
        # Pattern 3: Mixed single and double letters
        # Matches: "Te c h i n ca l"
        pattern3 = r'\b([a-z]{1,2})\s+([a-z]{1,2})\s+([a-z]{1,2})'
        for _ in range(5):
            prev_text = text
            text = re.sub(pattern3, r'\1\2\3', text, flags=re.IGNORECASE)
            if prev_text == text:
                break
        
        return text
    
    def fix_broken_words(self, text: str) -> str:
        """Fix common broken word patterns"""
        
        # Dictionary of common broken patterns -> correct words
        fixes = {
            # Common words in government documents
            r'\bt\s*e\s*c\s*h\s*n\s*i\s*c\s*a\s*l\b': 'technical',
            r'\bu\s*n\s*i\s*v\s*e\s*r\s*s\s*i\s*t\s*y\b': 'university',
            r'\bs\s*u\s*p\s*p\s*o\s*r\s*t\b': 'support',
            r'\bg\s*r\s*o\s*u\s*p\b': 'group',
            r'\bm\s*i\s*n\s*i\s*s\s*t\s*r\s*y\b': 'ministry',
            r'\bf\s*i\s*n\s*a\s*n\s*c\s*e\b': 'finance',
            r'\bm\s*i\s*n\s*i\s*s\s*t\s*e\s*r\b': 'minister',
            r'\be\s*d\s*u\s*c\s*a\s*t\s*i\s*o\s*n\b': 'education',
            r'\bd\s*e\s*v\s*e\s*l\s*o\s*p\s*m\s*e\s*n\s*t\b': 'development',
            r'\bg\s*o\s*v\s*e\s*r\s*n\s*m\s*e\s*n\s*t\b': 'government',
            r'\bp\s*h\s*y\s*s\s*i\s*c\s*a\s*l\b': 'physical',
            r'\bi\s*n\s*f\s*o\s*r\s*m\s*a\s*t\s*i\s*o\s*n\b': 'information',
            r'\bs\s*t\s*u\s*d\s*e\s*n\s*t\b': 'student',
            r'\bf\s*a\s*c\s*u\s*l\s*t\s*y\b': 'faculty',
            r'\bi\s*m\s*p\s*l\s*e\s*m\s*e\s*n\s*t\b': 'implement',
            r'\bi\s*n\s*s\s*t\s*i\s*t\s*u\s*t\s*i\s*o\s*n\b': 'institution',
            r'\bc\s*o\s*n\s*s\s*t\s*i\s*t\s*u\s*t\s*e\s*d\b': 'constituted',
            r'\ba\s*s\s*s\s*i\s*s\s*t\s*a\s*n\s*c\s*e\b': 'assistance',
            r'\bp\s*r\s*o\s*v\s*i\s*d\s*e\b': 'provide',
            r'\br\s*e\s*s\s*o\s*u\s*r\s*c\s*e\b': 'resource',
            r'\bh\s*u\s*m\s*a\s*n\b': 'human',
        }
        
        for pattern, replacement in fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def remove_extra_spaces(self, text: str) -> str:
        """Remove excessive whitespace while preserving structure"""
        # Multiple spaces to single space
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove space before punctuation
        text = re.sub(r'\s+([.,;:!?\)\]])', r'\1', text)
        
        # Add space after punctuation if missing
        text = re.sub(r'([.,;:!?\(\[])([A-Za-z0-9])', r'\1 \2', text)
        
        # Remove spaces around hyphens in words
        text = re.sub(r'(\w)\s+-\s+(\w)', r'\1-\2', text)
        
        # Clean up line breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 line breaks
        text = re.sub(r'\n ', '\n', text)  # Remove space after newline
        
        return text.strip()
    
    def fix_broken_hyphenations(self, text: str) -> str:
        """Fix words broken by hyphens at line breaks"""
        # Remove hyphen + newline/space + continue word
        text = re.sub(r'-\s*\n\s*', '', text)
        text = re.sub(r'-\s{2,}', '', text)
        
        return text
    
    def fix_common_ocr_errors(self, text: str) -> str:
        """Fix common OCR character misreads"""
        
        # Character-level fixes (only in word context)
        replacements = {
            # Common OCR confusions
            r'\brn\b': 'm',          # 'rn' -> 'm'
            r'\bvv\b': 'w',          # 'vv' -> 'w'
            r'\bl\b(?=[A-Z])': 'I',  # 'l' -> 'I' before uppercase
            r'(?<=[a-z])0(?=[a-z])': 'o',  # '0' -> 'o' between letters
            r'(?<=[a-z])1(?=[a-z])': 'l',  # '1' -> 'l' between letters
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def fix_unicode_issues(self, text: str) -> str:
        """Fix common unicode and special character issues"""
        fixes = {
            'ﬁ': 'fi',
            'ﬂ': 'fl',
            'ﬀ': 'ff',
            'ﬃ': 'ffi',
            'ﬄ': 'ffl',
            '–': '-',
            '—': '-',
            ''': "'",
            ''': "'",
            '"': '"',
            '"': '"',
            '…': '...',
            '•': '*',
            '◦': '-',
            '●': '*',
        }
        
        for wrong, correct in fixes.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def clean(self, text: str) -> str:
        """Apply all cleaning steps in order"""
        if not text:
            return ""
        
        # Step 1: Fix unicode issues first
        text = self.fix_unicode_issues(text)
        
        # Step 2: Fix broken hyphenations
        text = self.fix_broken_hyphenations(text)
        
        # Step 3: Fix common OCR character errors
        text = self.fix_common_ocr_errors(text)
        
        # Step 4: Fix spaced words (most important)
        text = self.fix_spaced_words(text)
        
        # Step 5: Fix known broken words
        text = self.fix_broken_words(text)
        
        # Step 6: Remove extra spaces (last step)
        text = self.remove_extra_spaces(text)
        
        return text


class PDFChunker:
    """Process MinerU parsed PDFs into semantic chunks with OCR cleaning"""
    
    def __init__(self, mongo_uri: str = "mongodb://admin:meow@localhost:27017/", db_name: str = "victor_rag"):
        """
        Initialize PDFChunker with MongoDB connection
        
        Args:
            mongo_uri: MongoDB connection URI (default: localhost:27017)
            db_name: Database name (default: victor_rag)
        """
        print(f"[INFO] Connecting to MongoDB: {mongo_uri}")
        self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # ✅ ADDED: Test connection
        try:
            self.client.server_info()
            print("[INFO] MongoDB connection successful")
        except Exception as e:
            print(f"[ERROR] MongoDB connection failed: {e}")
            print("[INFO] Continuing without MongoDB (will skip DB operations)")
            self.client = None
        
        if self.client:
            self.db = self.client[db_name]
            
            self.text_collection = self.db['text_chunks']
            self.table_collection = self.db['table_chunks']
            self.image_collection = self.db['image_chunks']
            self.metadata_collection = self.db['document_metadata']
            
            self._create_indexes()
        else:
            self.db = None
        
        self.ocr_cleaner = OCRTextCleaner()
        
        # Add these to accumulate chunks from all PDFs
        self.all_text_chunks = []
        self.all_table_chunks = []
        self.all_image_chunks = []
    
    def _create_indexes(self):
        """Create indexes for efficient querying"""
        if not self.client:
            return
        
        try:
            # Unique global ID index
            self.text_collection.create_index("global_chunk_id", unique=True)
            self.table_collection.create_index("global_chunk_id", unique=True)
            self.image_collection.create_index("global_chunk_id", unique=True)
            
            # Document and page indexes
            self.text_collection.create_index([("document_id", 1), ("page_idx", 1)])
            self.table_collection.create_index([("document_id", 1), ("page_idx", 1)])
            self.image_collection.create_index([("document_id", 1), ("page_idx", 1)])
            
            # Embedding status index
            self.text_collection.create_index("has_embedding")
            self.table_collection.create_index("has_embedding")
            self.image_collection.create_index("has_embedding")
            
            self.metadata_collection.create_index("document_name")
            
            print("[INFO] MongoDB indexes created successfully")
        except Exception as e:
            print(f"[WARN] Index creation warning: {e}")
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("[INFO] MongoDB connection closed")

    def _generate_global_id(self, document_id: str, chunk_type: str, chunk_index: int) -> str:
        """Generate globally unique chunk ID using UUID"""
        return str(uuid.uuid4())
    
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        return self.ocr_cleaner.clean(text)
    
    def _is_heading(self, block: Dict) -> bool:
        block_type = block.get('type', '')
        text = block.get('text', '').strip()
        
        if block_type == 'title':
            return True
        if block.get('text_level') is not None:
            return True
        if not text:
            return False
        if len(text) < 80 and '\n' not in text and text.isupper():
            return True
        if re.match(r'^(ITEM|AGENDA|CHAPTER|SECTION|PART|ANNEXURE)[\s\-\d]', text, re.IGNORECASE):
            return True
        if re.match(r'^\d+(\.\d+)*\.?\s+[A-Z]', text):
            return True
        return False
    
    def _is_paragraph_boundary(self, block1: Dict, block2: Dict) -> bool:
        if block1.get('page_idx') != block2.get('page_idx'):
            return True
        if self._is_heading(block1) or self._is_heading(block2):
            return True
        if block1.get('type') not in ['text', 'para'] or block2.get('type') not in ['text', 'para']:
            return True
        
        bbox1 = block1.get('bbox', [])
        bbox2 = block2.get('bbox', [])
        
        if len(bbox1) >= 4 and len(bbox2) >= 4:
            vertical_gap = bbox2[1] - bbox1[3]
            if vertical_gap > 40:
                return True
            indent_diff = abs(bbox1[0] - bbox2[0])
            if indent_diff > 20:
                return True
        
        text1 = block1.get('text', '').strip()
        if text1 and re.search(r'[.!?]\s*$', text1):
            text2 = block2.get('text', '').strip()
            if text2 and (text2[0].isupper() or text2[0].isdigit()):
                return True
        
        return False
    
    def _merge_bboxes(self, bboxes: List[List[int]]) -> List[int]:
        valid_bboxes = [bbox for bbox in bboxes if len(bbox) >= 4]
        if not valid_bboxes:
            return []
        return [
            min(bbox[0] for bbox in valid_bboxes),
            min(bbox[1] for bbox in valid_bboxes),
            max(bbox[2] for bbox in valid_bboxes),
            max(bbox[3] for bbox in valid_bboxes)
        ]
    
    def chunk_text_blocks(self, content_list: List[Dict], document_id: str, source_file: str) -> List[Dict]:
        """Extract and chunk text blocks with OCR cleaning"""
        text_chunks = []
        chunk_counter = 0
        heading_stack = []
        
        i = 0
        while i < len(content_list):
            block = content_list[i]
            block_type = block.get('type', '')
            
            if block_type in ['table', 'image', 'discarded']:
                i += 1
                continue
            
            text = block.get('text', '').strip()
            if not text:
                i += 1
                continue
            
            if self._is_heading(block):
                cleaned_heading = self._clean_text(text)
                heading_stack.append(cleaned_heading)
                if len(heading_stack) > 3:
                    heading_stack.pop(0)
                i += 1
                continue
            
            paragraph_blocks = [block]
            paragraph_texts = [text]
            bboxes = [block.get('bbox', [])]
            
            j = i + 1
            while j < len(content_list):
                next_block = content_list[j]
                if self._is_paragraph_boundary(block, next_block):
                    break
                next_text = next_block.get('text', '').strip()
                if next_text:
                    paragraph_blocks.append(next_block)
                    paragraph_texts.append(next_text)
                    bboxes.append(next_block.get('bbox', []))
                    block = next_block
                j += 1
            
            merged_text = ' '.join(paragraph_texts)
            cleaned_text = self._clean_text(merged_text)
            merged_bbox = self._merge_bboxes(bboxes)
            section_hierarchy = ' > '.join(heading_stack) if heading_stack else None
            
            global_id = self._generate_global_id(document_id, "text", chunk_counter)
            
            chunk = {
                "global_chunk_id": global_id,
                "document_id": document_id,
                "chunk_id": f"{document_id}_text_{chunk_counter}",
                "chunk_index": chunk_counter,
                "chunk_type": "text",
                "source_file": source_file,
                "page_idx": paragraph_blocks[0].get('page_idx', 0),
                "bbox": merged_bbox,
                "text": cleaned_text,
                "raw_text": merged_text,
                "section_hierarchy": section_hierarchy,
                "heading_context": heading_stack[-1] if heading_stack else None,
                "num_merged_blocks": len(paragraph_blocks),
                "char_count": len(cleaned_text),
                "word_count": len(cleaned_text.split()),
                "has_embedding": False,
                "embedding_model": None,
                "embedding_dimension": None,
                "created_at": datetime.utcnow(),
                "embedding_created_at": None
            }
            
            text_chunks.append(chunk)
            chunk_counter += 1
            i = j
        
        return text_chunks
    
    def _parse_html_table(self, html_table: str) -> Dict[str, Any]:
        if not html_table:
            return {"rows": [], "raw_html": ""}
        
        rows = re.findall(r'<tr>(.*?)</tr>', html_table, re.DOTALL)
        parsed_rows = []
        
        for row in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            cleaned_cells = [self._clean_text(cell) for cell in cells]
            if cleaned_cells:
                parsed_rows.append(cleaned_cells)
        
        return {
            "rows": parsed_rows,
            "num_rows": len(parsed_rows),
            "num_columns": len(parsed_rows[0]) if parsed_rows else 0,
            "raw_html": html_table
        }
    
    def chunk_tables(self, content_list: List[Dict], document_id: str, source_file: str) -> List[Dict]:
        """Extract table chunks with OCR cleaning"""
        table_chunks = []
        chunk_counter = 0
        
        for block in content_list:
            if block.get('type') != 'table':
                continue
            
            table_body = block.get('table_body', '')
            parsed_table = self._parse_html_table(table_body)
            
            caption = ' '.join(block.get('table_caption', []))
            footnote = ' '.join(block.get('table_footnote', []))
            
            table_text_parts = []
            if caption:
                table_text_parts.append(f"Caption: {self._clean_text(caption)}")
            for row in parsed_table['rows']:
                table_text_parts.append(' | '.join(row))
            if footnote:
                table_text_parts.append(f"Footnote: {self._clean_text(footnote)}")
            
            table_text = '\n'.join(table_text_parts)
            global_id = self._generate_global_id(document_id, "table", chunk_counter)
            
            chunk = {
                "global_chunk_id": global_id,
                "document_id": document_id,
                "chunk_id": f"{document_id}_table_{chunk_counter}",
                "chunk_index": chunk_counter,
                "chunk_type": "table",
                "source_file": source_file,
                "page_idx": block.get('page_idx', 0),
                "bbox": block.get('bbox', []),
                "img_path": block.get('img_path', ''),
                "table_data": parsed_table,
                "table_text": table_text,
                "caption": self._clean_text(caption),
                "footnote": self._clean_text(footnote),
                "has_embedding": False,
                "embedding_model": None,
                "embedding_dimension": None,
                "created_at": datetime.utcnow(),
                "embedding_created_at": None
            }
            
            table_chunks.append(chunk)
            chunk_counter += 1
        
        return table_chunks
    
    def chunk_images(self, content_list: List[Dict], document_id: str, source_file: str, base_path: str) -> List[Dict]:
        """Extract image chunks"""
        image_chunks = []
        chunk_counter = 0
        
        for block in content_list:
            if block.get('type') != 'image':
                continue
            
            img_path = block.get('img_path', '')
            if not img_path:
                continue
            
            full_img_path = os.path.join(base_path, img_path) if base_path else img_path
            caption = ' '.join(block.get('image_caption', []))
            global_id = self._generate_global_id(document_id, "image", chunk_counter)
            
            chunk = {
                "global_chunk_id": global_id,
                "document_id": document_id,
                "chunk_id": f"{document_id}_image_{chunk_counter}",
                "chunk_index": chunk_counter,
                "chunk_type": "image",
                "source_file": source_file,
                "page_idx": block.get('page_idx', 0),
                "bbox": block.get('bbox', []),
                "img_path": img_path,
                "full_img_path": full_img_path,
                "caption": self._clean_text(caption),
                "exists": os.path.exists(full_img_path) if full_img_path else False,
                "has_embedding": False,
                "embedding_model": None,
                "embedding_dimension": None,
                "created_at": datetime.utcnow(),
                "embedding_created_at": None
            }
            
            image_chunks.append(chunk)
            chunk_counter += 1
        
        return image_chunks
    
    def upload_from_json_files(self, chunked_outputs_dir: str):
        """
        Upload chunks from existing JSON files in chunked_outputs folder to MongoDB
        """
        print(f"\n🔄 Uploading chunks from JSON files to MongoDB...")
        print(f"Source directory: {chunked_outputs_dir}\n")
        
        chunked_path = Path(chunked_outputs_dir)
        if not chunked_path.exists():
            print(f"❌ Directory not found: {chunked_outputs_dir}")
            return
        
        stats = {
            "documents_processed": 0,
            "total_text_chunks": 0,
            "total_tables": 0,
            "total_images": 0,
            "failed": []
        }
        
        # Find all document folders
        for doc_folder in chunked_path.rglob("*"):
            if not doc_folder.is_dir():
                continue
            
            # Look for the three JSON files
            text_json = None
            tables_json = None
            images_json = None
            
            for json_file in doc_folder.glob("*.json"):
                if json_file.stem.endswith("_text"):
                    text_json = json_file
                elif json_file.stem.endswith("_tables"):
                    tables_json = json_file
                elif json_file.stem.endswith("_images"):
                    images_json = json_file
            
            # Skip if no JSON files found
            if not any([text_json, tables_json, images_json]):
                continue
            
            document_id = doc_folder.name
            print(f"📄 Uploading: {document_id}")
            
            try:
                # Load and upload text chunks
                text_count = 0
                if text_json and text_json.exists():
                    with open(text_json, 'r', encoding='utf-8') as f:
                        text_chunks = json.load(f)
                    if text_chunks:
                        # Delete existing
                        self.text_collection.delete_many({"document_id": document_id})
                        # Insert new
                        self.text_collection.insert_many(text_chunks)
                        text_count = len(text_chunks)
                        stats["total_text_chunks"] += text_count
                
                # Load and upload table chunks
                table_count = 0
                if tables_json and tables_json.exists():
                    with open(tables_json, 'r', encoding='utf-8') as f:
                        table_chunks = json.load(f)
                    if table_chunks:
                        self.table_collection.delete_many({"document_id": document_id})
                        self.table_collection.insert_many(table_chunks)
                        table_count = len(table_chunks)
                        stats["total_tables"] += table_count
                
                # Load and upload image chunks
                image_count = 0
                if images_json and images_json.exists():
                    with open(images_json, 'r', encoding='utf-8') as f:
                        image_chunks = json.load(f)
                    if image_chunks:
                        self.image_collection.delete_many({"document_id": document_id})
                        self.image_collection.insert_many(image_chunks)
                        image_count = len(image_chunks)
                        stats["total_images"] += image_count
                
                # Update metadata
                metadata = {
                    "document_id": document_id,
                    "document_name": document_id,
                    "source_file": str(doc_folder),
                    "total_text_chunks": text_count,
                    "total_tables": table_count,
                    "total_images": image_count,
                    "total_chunks": text_count + table_count + image_count,
                    "processed_at": datetime.utcnow(),
                    "embeddings_generated": False
                }
                
                self.metadata_collection.replace_one(
                    {"document_id": document_id},
                    metadata,
                    upsert=True
                )
                
                stats["documents_processed"] += 1
                print(f"  ✅ {text_count} text, {table_count} tables, {image_count} images")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                stats["failed"].append(document_id)
        
        # Print summary
        print(f"\n{'='*60}")
        print("📊 UPLOAD SUMMARY")
        print('='*60)
        print(f"Documents uploaded: {stats['documents_processed']}")
        print(f"Text chunks: {stats['total_text_chunks']}")
        print(f"Table chunks: {stats['total_tables']}")
        print(f"Image chunks: {stats['total_images']}")
        print(f"Failed: {len(stats['failed'])}")
        
        if stats['failed']:
            print("\n❌ Failed documents:")
            for doc in stats['failed']:
                print(f"  - {doc}")
    
    def process_pdf(self, content_list_path: str, output_dir: Optional[str] = None, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a single PDF with OCR cleaning"""
        print(f"\n📄 Processing: {Path(content_list_path).name}")
        
        with open(content_list_path, 'r', encoding='utf-8') as f:
            content_list = json.load(f)
        
        # ✅ FIXED: Use provided document_id or extract from filename as fallback
        if document_id is None:
            pdf_name = Path(content_list_path).stem.replace('_content_list', '')
            document_id = pdf_name
            print(f"⚠️  Using filename-based document_id: {document_id}")
        else:
            print(f"✅ Using provided document_id: {document_id}")
        
        base_path = os.path.dirname(content_list_path)
        source_file = str(Path(content_list_path).parent.parent.parent)
        
        print("  🧹 Cleaning OCR text...")
        text_chunks = self.chunk_text_blocks(content_list, document_id, source_file)
        
        print("  📊 Processing tables...")
        table_chunks = self.chunk_tables(content_list, document_id, source_file)
        
        print("  🖼️  Processing images...")
        image_chunks = self.chunk_images(content_list, document_id, source_file, base_path)
        
        # Accumulate chunks from all PDFs
        self.all_text_chunks.extend(text_chunks)
        self.all_table_chunks.extend(table_chunks)
        self.all_image_chunks.extend(image_chunks)
        
        # Still store in MongoDB per document
        stats = self._store_in_mongodb(document_id, document_id, text_chunks, table_chunks, image_chunks, base_path, source_file)
        return stats
    
    def _store_in_mongodb(self, document_id: str, pdf_name: str, 
                          text_chunks: List[Dict], table_chunks: List[Dict], 
                          image_chunks: List[Dict], base_path: str, source_file: str) -> Dict[str, Any]:
        """Store chunks in MongoDB"""
        
        # ✅ ADDED: Skip if MongoDB not connected
        if not self.client:
            print("[INFO] Skipping MongoDB storage (not connected)")
            return {
                "document_id": document_id,
                "text_chunks": len(text_chunks),
                "tables": len(table_chunks),
                "images": len(image_chunks)
            }
        
        try:
            self.text_collection.delete_many({"document_id": document_id})
            self.table_collection.delete_many({"document_id": document_id})
            self.image_collection.delete_many({"document_id": document_id})
            
            if text_chunks:
                self.text_collection.insert_many(text_chunks)
            if table_chunks:
                self.table_collection.insert_many(table_chunks)
            if image_chunks:
                self.image_collection.insert_many(image_chunks)
            
            metadata = {
                "document_id": document_id,
                "document_name": pdf_name,
                "source_file": source_file,
                "base_path": base_path,
                "total_text_chunks": len(text_chunks),
                "total_tables": len(table_chunks),
                "total_images": len(image_chunks),
                "total_chunks": len(text_chunks) + len(table_chunks) + len(image_chunks),
                "processed_at": datetime.utcnow(),
                "embeddings_generated": False
            }
            
            self.metadata_collection.replace_one(
                {"document_id": document_id},
                metadata,
                upsert=True
            )
            
            stats = {
                "document_id": document_id,
                "text_chunks": len(text_chunks),
                "tables": len(table_chunks),
                "images": len(image_chunks)
            }
            
            print(f"  [INFO] MongoDB: {stats['text_chunks']} text, {stats['tables']} tables, {stats['images']} images")
            return stats
            
        except Exception as e:
            print(f"  [ERROR] MongoDB error: {e}")
            raise
    
    def process_all_pdfs(self, outputs_dir: str, json_output_dir: Optional[str] = None, document_id: Optional[str] = None):
        """Process all PDFs and create consolidated JSON files"""
        print(f"�� Searching for PDFs in: {outputs_dir}")
        
        content_files = list(Path(outputs_dir).rglob("*_content_list.json"))
        
        if not content_files:
            print("❌ No content_list.json files found")
            return
        
        print(f"📚 Found {len(content_files)} PDF(s)\n")
        
        # ✅ FIXED: Use provided document_id or extract from path
        if document_id is None:
            # Fallback: try to extract from path structure
            # Path: backend/data/uploads/{document_id}/v{version}/outputs/...
            path_parts = Path(outputs_dir).parts
            if 'uploads' in path_parts:
                uploads_idx = path_parts.index('uploads')
                if uploads_idx + 1 < len(path_parts):
                    document_id = path_parts[uploads_idx + 1]
        
        if document_id is None:
            print("⚠️  WARNING: Could not determine document_id, using filename-based fallback")
        
        total_stats = {
            "total_pdfs": len(content_files),
            "total_text_chunks": 0,
            "total_tables": 0,
            "total_images": 0,
            "failed": []
        }
        
        # Reset accumulators
        self.all_text_chunks = []
        self.all_table_chunks = []
        self.all_image_chunks = []
        
        for content_file in content_files:
            try:
                # ✅ FIXED: Pass document_id to process_pdf
                stats = self.process_pdf(str(content_file), output_dir=None, document_id=document_id)
                
                total_stats["total_text_chunks"] += stats["text_chunks"]
                total_stats["total_tables"] += stats["tables"]
                total_stats["total_images"] += stats["images"]
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                import traceback
                traceback.print_exc()
                total_stats["failed"].append(str(content_file))
        
        # Save consolidated JSON files
        if json_output_dir:
            self._save_consolidated_json_files(json_output_dir)
        
        print(f"\n{'='*60}")
        print("📊 PROCESSING SUMMARY")
        print('='*60)
        print(f"PDFs processed: {total_stats['total_pdfs']}")
        print(f"Text chunks: {total_stats['total_text_chunks']}")
        print(f"Table chunks: {total_stats['total_tables']}")
        print(f"Image chunks: {total_stats['total_images']}")
        print(f"Failed: {len(total_stats['failed'])}")
    
    def _save_consolidated_json_files(self, json_output_dir: str):
        """Save all chunks to 3 consolidated JSON files"""
        print(f"\n💾 Saving consolidated JSON files to: {json_output_dir}")
        
        os.makedirs(json_output_dir, exist_ok=True)
        
        # Save all_text_chunks.json
        text_file = os.path.join(json_output_dir, "all_text_chunks.json")
        with open(text_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_text_chunks, f, indent=2, ensure_ascii=False, default=str)
        print(f"  ✅ Saved {len(self.all_text_chunks)} text chunks to all_text_chunks.json")
        
        # Save all_table_chunks.json
        table_file = os.path.join(json_output_dir, "all_table_chunks.json")
        with open(table_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_table_chunks, f, indent=2, ensure_ascii=False, default=str)
        print(f"  ✅ Saved {len(self.all_table_chunks)} table chunks to all_table_chunks.json")
        
        # Save all_image_chunks.json
        image_file = os.path.join(json_output_dir, "all_image_chunks.json")
        with open(image_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_image_chunks, f, indent=2, ensure_ascii=False, default=str)
        print(f"  ✅ Saved {len(self.all_image_chunks)} image chunks to all_image_chunks.json")
    
def main():
    """
    Main entry point for upload pipeline.
    Assumes script is run with cwd set to document version directory.
    """
    # ✅ FIXED: Get working directory from subprocess
    base_dir = Path(os.getcwd())
    
    print(f"[INFO] Working directory: {base_dir}")
    print(f"[INFO] Directory contents: {list(base_dir.iterdir())}")
    
    # ✅ FIXED: Extract document_id from working directory path
    # Path structure: backend/data/uploads/{document_id}/v{version}/
    # So document_id is the parent directory name
    document_id = base_dir.parent.name  # Gets the document_id from the path
    
    # Expected structure: base_dir/outputs/auto/content_list.json
    outputs_dir = base_dir / "outputs"
    json_output_dir = base_dir / "chunked_outputs_v2"
    
    if not outputs_dir.exists():
        print(f"[ERROR] Outputs directory not found: {outputs_dir}")
        sys.exit(1)
    
    # ✅ FIXED: Use localhost MongoDB
    MONGO_URI = "mongodb://admin:meow@localhost:27017/"
    DB_NAME = "victor_rag"
    
    try:
        chunker = PDFChunker(mongo_uri=MONGO_URI, db_name=DB_NAME)
        
        # ✅ FIXED: Pass document_id to process_all_pdfs
        chunker.process_all_pdfs(str(outputs_dir), str(json_output_dir), document_id=document_id)
        
        chunker.close()
        print("\n[INFO] Chunking complete!")
        sys.exit(0)
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()