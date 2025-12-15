"""
Milvus Collection Creator for Upload Pipeline
Creates hybrid collections (dense + sparse) from pipeline-generated embeddings
Adapted for upload pipeline working directory structure
"""

import sys
import io
import os
from pathlib import Path
import numpy as np
import json
from pymilvus import (
    connections, FieldSchema, CollectionSchema,
    DataType, Collection, utility, MilvusException
)
import time
from tqdm import tqdm
from scipy import sparse
import threading

# ✅ Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

# ✅ ADDED: Lock for Milvus collection operations
_collection_lock = threading.Lock()


def connect_milvus(retries=15, delay=6):
    """Connect to Milvus with retry logic"""
    for i in range(1, retries + 1):
        try:
            connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT, timeout=10)
            print(f"[INFO] Connected to Milvus at {MILVUS_HOST}:{MILVUS_PORT}")
            return True
        except MilvusException as e:
            print(f"[WARN] Retry {i}/{retries}: {e}")
            time.sleep(delay)
    
    print("[ERROR] Failed to connect to Milvus")
    return False


def collection_exists(name: str) -> bool:
    """Check if collection exists"""
    return utility.has_collection(name)


def get_or_create_text_collection(name: str = "VictorText2") -> Collection:
    """Get existing or create new text collection (thread-safe)"""
    with _collection_lock:
        if collection_exists(name):
            print(f"[INFO] Using existing collection: {name}")
            col = Collection(name)
            col.load()
            return col
        
        print(f"[INFO] Creating new text collection: {name}")
        
        # Get dimension from existing collection or use default
        try:
            # Try to get from embeddings file in cwd
            emb_path = Path.cwd() / "embeddings_consolidated" / "all_text_embeddings.npy"
            if emb_path.exists():
                embeddings = np.load(emb_path)
                dense_dim = embeddings.shape[1]
            else:
                dense_dim = 1024  # Default BGE-M3 dimension
        except:
            dense_dim = 1024
        
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="dense_embedding", dtype=DataType.FLOAT_VECTOR, dim=dense_dim),
            FieldSchema(name="sparse_embedding", dtype=DataType.SPARSE_FLOAT_VECTOR),
            FieldSchema(name="document_name", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="global_chunk_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="page_idx", dtype=DataType.INT32),
            FieldSchema(name="chunk_index", dtype=DataType.INT32),
            FieldSchema(name="section_hierarchy", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="heading_context", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="char_count", dtype=DataType.INT32),
            FieldSchema(name="word_count", dtype=DataType.INT32),
            FieldSchema(name="Category", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="document_type", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="ministry", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="published_date", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="source_reference", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="version", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="language", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="semantic_labels", dtype=DataType.VARCHAR, max_length=65535),
        ]
        
        schema = CollectionSchema(fields, description=f"{name} hybrid text collection")
        col = Collection(name, schema)
        
        # Create indexes
        dense_index_params = {
            "metric_type": "IP",
            "index_type": "HNSW",
            "params": {"M": 16, "efConstruction": 200}
        }
        col.create_index(field_name="dense_embedding", index_params=dense_index_params)
        
        sparse_index_params = {
            "metric_type": "IP",
            "index_type": "SPARSE_INVERTED_INDEX",
            "params": {"drop_ratio_build": 0.2}
        }
        col.create_index(field_name="sparse_embedding", index_params=sparse_index_params)
        
        col.load()
        print(f"[INFO] Created and indexed collection: {name}")
        return col


def get_or_create_table_collection(name: str = "VictorTable2") -> Collection:
    """Get existing or create new table collection (thread-safe)"""
    with _collection_lock:
        if collection_exists(name):
            print(f"[INFO] Using existing collection: {name}")
            col = Collection(name)
            col.load()
            return col
        
        print(f"[INFO] Creating new table collection: {name}")
        
        try:
            emb_path = Path.cwd() / "embeddings_consolidated" / "all_table_embeddings.npy"
            if emb_path.exists():
                embeddings = np.load(emb_path)
                dense_dim = embeddings.shape[1]
            else:
                dense_dim = 1024
        except:
            dense_dim = 1024
        
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="dense_embedding", dtype=DataType.FLOAT_VECTOR, dim=dense_dim),
            FieldSchema(name="sparse_embedding", dtype=DataType.SPARSE_FLOAT_VECTOR),
            FieldSchema(name="document_name", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="global_chunk_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="page_idx", dtype=DataType.INT32),
            FieldSchema(name="table_index", dtype=DataType.INT32),
            FieldSchema(name="section_hierarchy", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="heading_context", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="table_text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="table_markdown", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="table_html", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="caption", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="row_count", dtype=DataType.INT32),
            FieldSchema(name="col_count", dtype=DataType.INT32),
            FieldSchema(name="Category", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="document_type", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="ministry", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="published_date", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="source_reference", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="version", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="language", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="semantic_labels", dtype=DataType.VARCHAR, max_length=65535),
        ]
        
        schema = CollectionSchema(fields, description=f"{name} hybrid table collection")
        col = Collection(name, schema)
        
        # Create indexes
        dense_index_params = {
            "metric_type": "IP",
            "index_type": "HNSW",
            "params": {"M": 16, "efConstruction": 200}
        }
        col.create_index(field_name="dense_embedding", index_params=dense_index_params)
        
        sparse_index_params = {
            "metric_type": "IP",
            "index_type": "SPARSE_INVERTED_INDEX",
            "params": {"drop_ratio_build": 0.2}
        }
        col.create_index(field_name="sparse_embedding", index_params=sparse_index_params)
        
        col.load()
        print(f"[INFO] Created and indexed collection: {name}")
        return col


def safe_truncate(text: str, max_length: int) -> str:
    """Safely truncate text to max_length BYTES"""
    if not text:
        return ''
    
    text_str = str(text)
    text_bytes = text_str.encode('utf-8')
    
    if len(text_bytes) <= max_length:
        return text_str
    
    truncated_bytes = text_bytes[:max_length]
    
    try:
        return truncated_bytes.decode('utf-8')
    except UnicodeDecodeError:
        for i in range(1, 5):
            try:
                return truncated_bytes[:-i].decode('utf-8')
            except UnicodeDecodeError:
                continue
        return truncated_bytes.decode('utf-8', errors='ignore')


def load_sparse_npz(npz_path: Path):
    """Load sparse embeddings from NPZ file"""
    print(f"[INFO] Loading sparse embeddings from {npz_path.name}")
    
    data = np.load(npz_path, allow_pickle=True)
    
    indices = data['indices']
    values = data['values']
    indptr = data['indptr']
    shape = data['shape']
    metadata = data['metadata']
    
    csr_matrix = sparse.csr_matrix(
        (values, indices, indptr),
        shape=(shape[0], shape[1])
    )
    
    print(f"   Loaded {csr_matrix.shape[0]} sparse embeddings")
    
    return csr_matrix, metadata


def csr_row_to_sparse_dict(csr_matrix, row_idx: int) -> dict:
    """Convert CSR row to Milvus sparse dict format"""
    start = csr_matrix.indptr[row_idx]
    end = csr_matrix.indptr[row_idx + 1]
    
    indices = csr_matrix.indices[start:end]
    values = csr_matrix.data[start:end]
    
    return {int(idx): float(val) for idx, val in zip(indices, values)}


def build_global_chunk_id_mapping(sparse_metadata):
    """Build mapping from global_chunk_id to sparse embedding index"""
    mapping = {}
    for idx, meta in enumerate(sparse_metadata):
        if isinstance(meta, dict):
            global_id = meta.get('global_chunk_id')
        elif hasattr(meta, 'item'):
            global_id = meta.item().get('global_chunk_id')
        else:
            global_id = None
        
        if global_id:
            mapping[global_id] = idx
    
    return mapping


def load_dense_metadata(metadata_path: Path):
    """Load metadata from dense embeddings to get the order"""
    print(f"[INFO] Loading dense embedding metadata from {metadata_path.name}")
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print(f"   Raw metadata type: {type(metadata)}")
    
    # ✅ FIXED: Handle all possible formats
    dense_global_ids = {}
    
    # ✅ NEW: Handle dict with "chunks" key (from embedding_creator.py)
    if isinstance(metadata, dict) and "chunks" in metadata:
        print(f"   [INFO] Metadata format: dict with 'chunks' array")
        chunks_list = metadata["chunks"]
        print(f"   Loaded {len(chunks_list)} chunks from metadata")
        
        for idx, chunk_meta in enumerate(chunks_list):
            global_chunk_id = chunk_meta.get('global_chunk_id')
            if global_chunk_id:
                dense_global_ids[global_chunk_id] = idx
            else:
                # Fallback: use embedding_index if available
                embedding_idx = chunk_meta.get('embedding_index', idx)
                # Try to get global_chunk_id from chunk_id or document_id
                chunk_id = chunk_meta.get('chunk_id')
                if chunk_id:
                    dense_global_ids[chunk_id] = embedding_idx
    
    elif isinstance(metadata, list):
        print(f"   Loaded {len(metadata)} metadata entries (list)")
        
        if metadata and isinstance(metadata[0], str):
            print(f"   [INFO] Metadata format: list of global_chunk_ids")
            dense_global_ids = {chunk_id: idx for idx, chunk_id in enumerate(metadata)}
            
        elif metadata and isinstance(metadata[0], dict):
            print(f"   [INFO] Metadata format: list of metadata dicts")
            dense_global_ids = {meta['global_chunk_id']: idx for idx, meta in enumerate(metadata) if meta.get('global_chunk_id')}
        
        else:
            print(f"   [WARN] Unknown list format, first element: {type(metadata[0]) if metadata else 'empty'}")
    
    elif isinstance(metadata, dict):
        print(f"   Loaded {len(metadata)} metadata entries (dict)")
        
        # Skip if it's the chunks format (already handled above)
        if "chunks" not in metadata:
            first_key = next(iter(metadata.keys()))
            first_value = metadata[first_key]
            
            if isinstance(first_value, str):
                print(f"   [INFO] Metadata format: dict of index->global_chunk_id")
                dense_global_ids = {chunk_id: int(idx) for idx, chunk_id in metadata.items()}
                
            elif isinstance(first_value, dict):
                print(f"   [INFO] Metadata format: dict of global_chunk_id->metadata")
                dense_global_ids = {chunk_id: idx for idx, chunk_id in enumerate(metadata.keys())}
            
            else:
                print(f"   [WARN] Unknown dict format, first value type: {type(first_value)}")
    
    else:
        print(f"   [ERROR] Unknown metadata type: {type(metadata)}")
    
    print(f"   [INFO] Built mapping for {len(dense_global_ids)} chunks")
    
    if len(dense_global_ids) > 0:
        sample = dict(list(dense_global_ids.items())[:3])
        print(f"   [DEBUG] Sample mapping: {sample}")
    else:
        print(f"   [ERROR] ⚠️  No global_chunk_ids found in metadata!")
        print(f"   [DEBUG] Metadata keys: {list(metadata.keys()) if isinstance(metadata, dict) else 'N/A'}")
    
    return dense_global_ids


def insert_text_chunks():
    """Insert text chunks into VictorText2"""
    print("\n" + "="*60)
    print("[INFO] Processing Text Chunks")
    print("="*60)
    
    base_path = Path.cwd()
    dense_emb_path = base_path / "embeddings_consolidated" / "all_text_embeddings.npy"
    dense_meta_path = base_path / "embeddings_consolidated" / "all_text_metadata.json"
    chunks_path = base_path / "chunked_outputs_v2" / "all_text_chunks.json"
    sparse_npz_path = base_path / "sparse_embeddings" / "text_sparse_embeddings.npz"
    
    # Check files exist
    if not dense_emb_path.exists():
        print(f"[SKIP] Dense embeddings not found: {dense_emb_path}")
        return
    if not dense_meta_path.exists():
        print(f"[SKIP] Dense metadata not found: {dense_meta_path}")
        return
    if not chunks_path.exists():
        print(f"[SKIP] Chunks JSON not found: {chunks_path}")
        return
    if not sparse_npz_path.exists():
        print(f"[SKIP] Sparse embeddings not found: {sparse_npz_path}")
        return
    
    # Load data
    print(f"[INFO] Loading dense embeddings...")
    dense_embeddings = np.load(dense_emb_path)
    print(f"   {dense_embeddings.shape[0]} embeddings, dim={dense_embeddings.shape[1]}")
    
    # ✅ FIXED: Load dense metadata (now returns dict directly)
    dense_global_ids = load_dense_metadata(dense_meta_path)
    
    # ✅ ADDED: Debug logging
    print(f"   [DEBUG] Dense metadata loaded: {len(dense_global_ids)} mappings")
    if len(dense_global_ids) > 0:
        sample_ids = list(dense_global_ids.keys())[:3]
        print(f"   [DEBUG] Sample global_chunk_ids from metadata: {sample_ids}")
    
    print(f"[INFO] Loading chunks...")
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"   {len(chunks)} chunks")
    
    # ✅ ADDED: Debug logging for chunks
    if len(chunks) > 0:
        sample_chunk_ids = [chunk.get('global_chunk_id') for chunk in chunks[:3]]
        print(f"   [DEBUG] Sample global_chunk_ids from chunks: {sample_chunk_ids}")
    
    sparse_csr, sparse_metadata = load_sparse_npz(sparse_npz_path)
    sparse_id_mapping = build_global_chunk_id_mapping(sparse_metadata)
    
    # ✅ ADDED: Debug logging for sparse
    print(f"   [DEBUG] Sparse metadata loaded: {len(sparse_id_mapping)} mappings")
    if len(sparse_id_mapping) > 0:
        sample_sparse_ids = list(sparse_id_mapping.keys())[:3]
        print(f"   [DEBUG] Sample global_chunk_ids from sparse: {sample_sparse_ids}")
    
    # Get or create collection
    col = get_or_create_text_collection()
    
    # ✅ FIXED: Only process chunks that have BOTH dense and sparse embeddings
    valid_chunks = []
    valid_dense_embeddings = []
    valid_sparse_embeddings = []
    valid_metadata = []
    
    skipped_no_dense = 0
    skipped_no_sparse = 0
    
    print("[INFO] Matching chunks with embeddings...")
    for chunk in tqdm(chunks, desc="Processing chunks"):
        global_chunk_id = chunk.get('global_chunk_id', '')
        
        # Check if chunk has dense embedding
        dense_idx = dense_global_ids.get(global_chunk_id)
        if dense_idx is None:
            skipped_no_dense += 1
            continue
        
        # Check if chunk has sparse embedding
        sparse_idx = sparse_id_mapping.get(global_chunk_id)
        if sparse_idx is None:
            skipped_no_sparse += 1
            continue
        
        # ✅ Both embeddings exist - add to valid list
        valid_chunks.append(chunk)
        valid_dense_embeddings.append(dense_embeddings[dense_idx])
        
        sparse_dict = csr_row_to_sparse_dict(sparse_csr, sparse_idx)
        valid_sparse_embeddings.append(sparse_dict)
        
        # Prepare metadata
        semantic_labels = chunk.get('semantic_labels', {})
        semantic_labels_str = json.dumps(semantic_labels) if isinstance(semantic_labels, dict) else str(semantic_labels)
        
        valid_metadata.append({
            'document_name': safe_truncate(
                chunk.get('document_name') or chunk.get('document_id') or chunk.get('source', 'unknown'), 
                512
            ),
            'document_id': safe_truncate(chunk.get('document_id', 'unknown'), 256),
            'chunk_id': safe_truncate(chunk.get('chunk_id', f'text_{dense_idx}'), 256),
            'global_chunk_id': safe_truncate(global_chunk_id, 256),
            'page_idx': int(chunk.get('page_idx', chunk.get('page', 0))),
            'chunk_index': int(chunk.get('chunk_index', dense_idx)),
            'section_hierarchy': safe_truncate(chunk.get('section_hierarchy', ''), 65535),
            'heading_context': safe_truncate(chunk.get('heading_context', ''), 65535),
            'text': safe_truncate(chunk.get('text', ''), 65535),
            'char_count': int(chunk.get('char_count', len(chunk.get('text', '')))),
            'word_count': int(chunk.get('word_count', len(chunk.get('text', '').split()))),
            'Category': safe_truncate(chunk.get('Category', ''), 1024),
            'document_type': safe_truncate(chunk.get('document_type', ''), 1024),
            'ministry': safe_truncate(chunk.get('ministry', ''), 1024),
            'published_date': safe_truncate(chunk.get('published_date', '') or '', 256),
            'source_reference': safe_truncate(chunk.get('source_reference', ''), 1024),
            'version': safe_truncate(chunk.get('version', '') or '', 128),
            'language': safe_truncate(chunk.get('language', 'english'), 128),
            'semantic_labels': safe_truncate(semantic_labels_str, 65535),
        })
    
    # Convert to numpy array
    valid_dense_embeddings = np.array(valid_dense_embeddings)
    
    print(f"[INFO] Valid chunks with both embeddings: {len(valid_chunks)}")
    if skipped_no_dense > 0:
        print(f"[WARN] Chunks without dense embedding: {skipped_no_dense}")
    if skipped_no_sparse > 0:
        print(f"[WARN] Chunks without sparse embedding: {skipped_no_sparse}")
    
    if len(valid_chunks) == 0:
        print("[WARN] No valid chunks to insert!")
        return
    
    # Insert in batches
    batch_size = 1000
    total = len(valid_metadata)
    
    print("[INFO] Inserting into Milvus...")
    for i in tqdm(range(0, total, batch_size), desc="Inserting batches"):
        end = min(i + batch_size, total)
        
        batch_data = [
            valid_dense_embeddings[i:end].tolist(),
            valid_sparse_embeddings[i:end],
            [m['document_name'] for m in valid_metadata[i:end]],
            [m['document_id'] for m in valid_metadata[i:end]],
            [m['chunk_id'] for m in valid_metadata[i:end]],
            [m['global_chunk_id'] for m in valid_metadata[i:end]],
            [m['page_idx'] for m in valid_metadata[i:end]],
            [m['chunk_index'] for m in valid_metadata[i:end]],
            [m['section_hierarchy'] for m in valid_metadata[i:end]],
            [m['heading_context'] for m in valid_metadata[i:end]],
            [m['text'] for m in valid_metadata[i:end]],
            [m['char_count'] for m in valid_metadata[i:end]],
            [m['word_count'] for m in valid_metadata[i:end]],
            [m['Category'] for m in valid_metadata[i:end]],
            [m['document_type'] for m in valid_metadata[i:end]],
            [m['ministry'] for m in valid_metadata[i:end]],
            [m['published_date'] for m in valid_metadata[i:end]],
            [m['source_reference'] for m in valid_metadata[i:end]],
            [m['version'] for m in valid_metadata[i:end]],
            [m['language'] for m in valid_metadata[i:end]],
            [m['semantic_labels'] for m in valid_metadata[i:end]],
        ]
        
        col.insert(batch_data)
    
    col.flush()
    print(f"[INFO] Inserted {len(valid_metadata)} text entities")
    print(f"[INFO] Collection now has {col.num_entities} total entities")
    
    # ✅ ADDED: Reload collection to make new data searchable immediately
    col.load()
    print(f"[INFO] Collection reloaded - new data is now searchable")


def insert_table_chunks():
    """Insert table chunks into VictorTable2"""
    print("\n" + "="*60)
    print("[INFO] Processing Table Chunks")
    print("="*60)
    
    base_path = Path.cwd()
    dense_emb_path = base_path / "embeddings_consolidated" / "all_table_embeddings.npy"
    dense_meta_path = base_path / "embeddings_consolidated" / "all_table_metadata.json"
    chunks_path = base_path / "chunked_outputs_v2" / "all_table_chunks.json"
    sparse_npz_path = base_path / "sparse_embeddings" / "table_sparse_embeddings.npz"
    
    if not dense_emb_path.exists():
        print(f"[SKIP] Dense embeddings not found: {dense_emb_path}")
        return
    if not dense_meta_path.exists():
        print(f"[SKIP] Dense metadata not found: {dense_meta_path}")
        return
    if not chunks_path.exists():
        print(f"[SKIP] Chunks JSON not found: {chunks_path}")
        return
    if not sparse_npz_path.exists():
        print(f"[SKIP] Sparse embeddings not found: {sparse_npz_path}")
        return
    
    print(f"[INFO] Loading dense embeddings...")
    dense_embeddings = np.load(dense_emb_path)
    print(f"   {dense_embeddings.shape[0]} embeddings, dim={dense_embeddings.shape[1]}")
    
    # ✅ FIXED: Use updated load_dense_metadata
    dense_global_ids = load_dense_metadata(dense_meta_path)
    
    print(f"[INFO] Loading chunks...")
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"   {len(chunks)} chunks")
    
    sparse_csr, sparse_metadata = load_sparse_npz(sparse_npz_path)
    sparse_id_mapping = build_global_chunk_id_mapping(sparse_metadata)
    
    col = get_or_create_table_collection()
    
    # ✅ FIXED: Same matching logic as text chunks
    valid_chunks = []
    valid_dense_embeddings = []
    valid_sparse_embeddings = []
    valid_metadata = []
    
    skipped_no_dense = 0
    skipped_no_sparse = 0
    
    print("[INFO] Matching chunks with embeddings...")
    for chunk in tqdm(chunks, desc="Processing chunks"):
        global_chunk_id = chunk.get('global_chunk_id', '')
        
        dense_idx = dense_global_ids.get(global_chunk_id)
        if dense_idx is None:
            skipped_no_dense += 1
            continue
        
        sparse_idx = sparse_id_mapping.get(global_chunk_id)
        if sparse_idx is None:
            skipped_no_sparse += 1
            continue
        
        valid_chunks.append(chunk)
        valid_dense_embeddings.append(dense_embeddings[dense_idx])
        
        sparse_dict = csr_row_to_sparse_dict(sparse_csr, sparse_idx)
        valid_sparse_embeddings.append(sparse_dict)
        
        semantic_labels = chunk.get('semantic_labels', {})
        semantic_labels_str = json.dumps(semantic_labels) if isinstance(semantic_labels, dict) else str(semantic_labels)
        
        valid_metadata.append({
            'document_name': safe_truncate(chunk.get('document_name', chunk.get('source', 'unknown')), 512),
            'document_id': safe_truncate(chunk.get('document_id', 'unknown'), 256),
            'chunk_id': safe_truncate(chunk.get('chunk_id', f'table_{dense_idx}'), 256),
            'global_chunk_id': safe_truncate(global_chunk_id, 256),
            'page_idx': int(chunk.get('page_idx', chunk.get('page', 0))),
            'table_index': int(chunk.get('table_index', dense_idx)),
            'section_hierarchy': safe_truncate(chunk.get('section_hierarchy', ''), 65535),
            'heading_context': safe_truncate(chunk.get('heading_context', ''), 65535),
            'table_text': safe_truncate(chunk.get('table_text', chunk.get('text', '')), 65535),
            'table_markdown': safe_truncate(chunk.get('table_markdown', ''), 65535),
            'table_html': safe_truncate(chunk.get('table_html', ''), 65535),
            'caption': safe_truncate(chunk.get('caption', ''), 65535),
            'row_count': int(chunk.get('row_count', 0)),
            'col_count': int(chunk.get('col_count', 0)),
            'Category': safe_truncate(chunk.get('Category', ''), 1024),
            'document_type': safe_truncate(chunk.get('document_type', ''), 1024),
            'ministry': safe_truncate(chunk.get('ministry', ''), 1024),
            'published_date': safe_truncate(chunk.get('published_date', '') or '', 256),
            'source_reference': safe_truncate(chunk.get('source_reference', ''), 1024),
            'version': safe_truncate(chunk.get('version', '') or '', 128),
            'language': safe_truncate(chunk.get('language', 'english'), 128),
            'semantic_labels': safe_truncate(semantic_labels_str, 65535),
        })
    
    valid_dense_embeddings = np.array(valid_dense_embeddings)
    
    print(f"[INFO] Valid tables with both embeddings: {len(valid_chunks)}")
    if skipped_no_dense > 0:
        print(f"[WARN] Tables without dense embedding: {skipped_no_dense}")
    if skipped_no_sparse > 0:
        print(f"[WARN] Tables without sparse embedding: {skipped_no_sparse}")
    
    if len(valid_chunks) == 0:
        print("[WARN] No valid tables to insert!")
        return
    
    batch_size = 1000
    total = len(valid_metadata)
    
    print("[INFO] Inserting into Milvus...")
    for i in tqdm(range(0, total, batch_size), desc="Inserting batches"):
        end = min(i + batch_size, total)
        
        batch_data = [
            valid_dense_embeddings[i:end].tolist(),
            valid_sparse_embeddings[i:end],
            [m['document_name'] for m in valid_metadata[i:end]],
            [m['document_id'] for m in valid_metadata[i:end]],
            [m['chunk_id'] for m in valid_metadata[i:end]],
            [m['global_chunk_id'] for m in valid_metadata[i:end]],
            [m['page_idx'] for m in valid_metadata[i:end]],
            [m['table_index'] for m in valid_metadata[i:end]],
            [m['section_hierarchy'] for m in valid_metadata[i:end]],
            [m['heading_context'] for m in valid_metadata[i:end]],
            [m['table_text'] for m in valid_metadata[i:end]],
            [m['table_markdown'] for m in valid_metadata[i:end]],
            [m['table_html'] for m in valid_metadata[i:end]],
            [m['caption'] for m in valid_metadata[i:end]],
            [m['row_count'] for m in valid_metadata[i:end]],
            [m['col_count'] for m in valid_metadata[i:end]],
            [m['Category'] for m in valid_metadata[i:end]],
            [m['document_type'] for m in valid_metadata[i:end]],
            [m['ministry'] for m in valid_metadata[i:end]],
            [m['published_date'] for m in valid_metadata[i:end]],
            [m['source_reference'] for m in valid_metadata[i:end]],
            [m['version'] for m in valid_metadata[i:end]],
            [m['language'] for m in valid_metadata[i:end]],
            [m['semantic_labels'] for m in valid_metadata[i:end]],
        ]
        
        col.insert(batch_data)
    
    col.flush()
    print(f"[INFO] Inserted {len(valid_metadata)} table entities")
    print(f"[INFO] Collection now has {col.num_entities} total entities")
    
    # ✅ ADDED: Reload collection to make new data searchable immediately
    col.load()
    print(f"[INFO] Collection reloaded - new data is now searchable")


def main():
    """Main execution for upload pipeline"""
    print("\n" + "="*60)
    print("[INFO] Milvus Upload Pipeline Ingestion")
    print("="*60)
    print(f"[INFO] Working directory: {Path.cwd()}")
    
    if not connect_milvus():
        print("[ERROR] Cannot connect to Milvus")
        sys.exit(1)
    
    try:
        insert_text_chunks()
        insert_table_chunks()
        
        print("\n" + "="*60)
        print("[INFO] Upload pipeline ingestion complete!")
        print("="*60)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"[ERROR] Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()