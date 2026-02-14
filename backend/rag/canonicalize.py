# backend/rag/canonicalize.py
import hashlib
import json
import unicodedata
from typing import Dict, List


class FatalError(Exception):
    pass


def canonicalize_text(text: str) -> str:
    """
    Canonicalize raw extracted text into a normalized format
    for downstream chunking and indexing.
    """
    if not text:
        return ""

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    return "\n".join(lines)


def get_canonical_hash(chunk: Dict) -> str:
    text = unicodedata.normalize("NFKC", chunk["text"].strip())
    text = " ".join(text.split())

    canonical_obj = {
        "doc_id": chunk["doc_id"],
        "text": text,
        "page": chunk["page"],
        "line_start": chunk["line_start"],
        "line_end": chunk["line_end"],
    }

    raw = json.dumps(canonical_obj, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def deduplicate_chunks(chunks: List[Dict], existing_hashes: set) -> List[Dict]:
    unique = []

    for chunk in chunks:
        h = get_canonical_hash(chunk)

        if h in existing_hashes:
            raise FatalError(f"DUPLICATE_CHUNK_DETECTED: {h}")

        existing_hashes.add(h)
        chunk["content_hash"] = h
        unique.append(chunk)

    return unique
