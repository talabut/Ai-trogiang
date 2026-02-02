import hashlib
from datetime import datetime
from llama_index.core.schema import TextNode

INGEST_VERSION = "v1.0"
EMBEDDING_MODEL_TAG = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

def compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def convert_chunks_to_nodes(chunks, document_id, file_name):
    nodes = []
    for chunk in chunks:
        text = chunk["text"].strip()
        if not text:
            continue

        h = compute_content_hash(text)
        node = TextNode(
            id_=h,
            text=text,
            metadata={
                "doc_id": document_id,
                "file_name": file_name,
                "content_hash": h,
                "index_version": INGEST_VERSION,
                "embedding_model": EMBEDDING_MODEL_TAG,
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
                "ingest_time": datetime.utcnow().isoformat(),
            },
        )
        nodes.append(node)
    return nodes
