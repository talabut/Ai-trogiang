# FILE: backend/rag/node_parser.py
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from llama_index.core.schema import TextNode

# Configuration
INGEST_VERSION = "v1.0"
EMBEDDING_MODEL_TAG = "sentence-transformers/all-MiniLM-L6-v2"

def compute_content_hash(text: str) -> str:
    """Generate SHA256 hash for text content to detect duplicates."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def convert_chunks_to_nodes(
    chunks: List[Dict[str, Any]], 
    document_id: str,
    file_name: str
) -> List[TextNode]:
    """
    Convert Chunk Dicts to LlamaIndex TextNodes with strict metadata mapping.
    One Chunk = One TextNode.
    """
    nodes = []
    
    for chunk in chunks:
        # 1. Validate Input
        text_content = chunk.get("text", "")
        if not text_content.strip():
            continue
            
        content_hash = compute_content_hash(text_content)
        
        # 2. Build Strict Metadata (Page + Lines)
        metadata = {
            "doc_id": document_id,
            "file_name": file_name,
            "page": chunk.get("page"),           # Strict: must be present
            "line_start": chunk.get("line_start"),
            "line_end": chunk.get("line_end"),
            "source": chunk.get("sources", ["unknown"])[0] if "sources" in chunk else "unknown",
            "content_hash": content_hash,
            "ingest_time": datetime.utcnow().isoformat(),
            "index_version": INGEST_VERSION,
            "embedding_model": EMBEDDING_MODEL_TAG
        }

        # 3. Create TextNode
        # Use content_hash as ID for system-level deduplication capability
        node = TextNode(
            text=text_content,
            id_=content_hash, 
            metadata=metadata
        )
        
        # 4. Exclude metadata from Embedding and LLM context to save tokens/noise
        # Embedding sees only text (and maybe context if configured, but keeping it clean here)
        node.excluded_embed_metadata_keys = [
            "ingest_time", "index_version", "content_hash", 
            "line_start", "line_end", "embedding_model", "doc_id", "page", "file_name", "source"
        ]
        # LLM sees text + minimal context (page, source)
        node.excluded_llm_metadata_keys = [
            "content_hash", "index_version", "embedding_model", "ingest_time", "doc_id"
        ]

        nodes.append(node)

    return nodes