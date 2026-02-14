# backend/rag/chunking.py
import threading
import hashlib
from typing import List

_ingest_lock = threading.Lock()
_seen_hashes = set()


def ingest_with_lock(text: str, func):
    """
    Ensure the same text is ingested only once (process-wide).
    Deterministic via SHA-256 hash.
    """
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()

    with _ingest_lock:
        if h in _seen_hashes:
            return {"status": "skipped"}

        _seen_hashes.add(h)
        func(text)
        return {"status": "ingested"}


def strict_chunk_text(text: str) -> List[str]:
    """
    Strict deterministic text chunker.

    - Input: raw text (str)
    - Output: List[str] of clean chunks

    Rules:
    - Split by lines
    - Strip whitespace
    - Drop empty lines
    - Preserve order
    - No metadata, no side effects
    """
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def chunk_canonical_data(text: str, doc_id: str):
    """
    Strict deterministic chunker for tests.
    Produces canonical chunks with metadata.
    """
    lines = text.splitlines()
    chunks = []

    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        chunks.append({
            "text": line.strip(),
            "doc_id": doc_id,
            "page": 1,
            "line_start": i,
            "line_end": i,
        })

    return chunks
