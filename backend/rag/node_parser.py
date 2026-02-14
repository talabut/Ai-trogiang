
from typing import List, Dict, Any
from backend.rag.chunking import strict_chunk_text


# === Ingest / Vectorstore contract constants ===
INGEST_VERSION = "v1"
EMBEDDING_MODEL_TAG = "default"

# Chunking contract (MUST match chunking.py)
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

def parse_nodes(
    text: str,
    file_name: str,
    metadata_pages: List[Dict[str, Any]],
):
    """
    Mỗi node BẮT BUỘC có:
    - page
    - line_start
    - line_end
    - file_name
    """

    assert isinstance(text, str)
    assert file_name

    nodes = []
    chunks = strict_chunk_text(text)

    for chunk in chunks:
        page_meta = _match_page_metadata(chunk, metadata_pages)

        assert page_meta is not None, "Missing OCR metadata"

        nodes.append({
            "text": chunk,
            "metadata": {
                "page": page_meta["page"],
                "line_start": page_meta["line_start"],
                "line_end": page_meta["line_end"],
                "file_name": file_name,
            },
        })

    return nodes


def _match_page_metadata(chunk: str, pages: List[Dict[str, Any]]):
    for page in pages:
        if page["text"] in chunk:
            return page
    return None
