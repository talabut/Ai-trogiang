from typing import List, Dict, Any
from backend.rag.chunking import chunk_single_text

# === Ingest / Vectorstore contract constants ===
INGEST_VERSION = "v1"
EMBEDDING_MODEL_TAG = "default"

# Chunking contract (must align with chunking.py config)
CHUNK_SIZE = 512
CHUNK_OVERLAP = 100


def parse_nodes(
    chunks: List[Dict[str, Any]],
    file_name: str,
):
    """
    Each node must include:
    - page
    - start_char
    - end_char
    - chunk_id
    - index_version
    - file_name
    """

    assert isinstance(chunks, list)
    assert file_name

    nodes = []

    for i, chunk in enumerate(chunks):

        chunk_text_value = chunk["text"]

        nodes.append({
            "text": chunk_text_value,
            "metadata": {
                "page": chunk.get("page", 1),
                "start_char": 0,  # simplified for now
                "end_char": len(chunk_text_value),
                "chunk_id": f"{file_name}_{i}",
                "index_version": INGEST_VERSION,
                "file_name": file_name,
            },
        })

    return nodes