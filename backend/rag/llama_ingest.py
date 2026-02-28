import os
import json
import logging
from typing import List, Dict, Any

from backend.rag.canonicalize import canonicalize_text, get_canonical_hash
from backend.config.integrity_config import settings

INDEX_VERSION = "v1.0"
EMBEDDING_MODEL_TAG = "sentence-transformers/all-MiniLM-L6-v2"

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    Approximate token count.
    MiniLM ~ 1 token ≈ 0.75 words (rough estimate).
    """
    if not text:
        return 0
    return int(len(text.split()) / 0.75)


def get_index_path(course_id: str) -> str:
    """
    Unified FAISS persist directory.
    MUST match retrieval layer.
    """
    return os.path.join(settings.FAISS_INDEX_DIR, course_id)


def _ensure_index_meta(path: str, course_id: str):
    """
    Ensure index_meta.json exists and is consistent.
    """
    meta_path = os.path.join(path, "index_meta.json")

    meta = {
        "course_id": course_id,
        "index_version": INDEX_VERSION,
        "embedding_model_tag": EMBEDDING_MODEL_TAG
    }

    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            # Fail fast if mismatch
            if (
                existing.get("embedding_model_tag") != EMBEDDING_MODEL_TAG
                or existing.get("index_version") != INDEX_VERSION
            ):
                raise RuntimeError("INDEX_META_MISMATCH")
        except json.JSONDecodeError:
            pass

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def ingest_canonical_chunks(
    chunks: List[Dict[str, Any]],
    course_id: str,
    filename: str,
    doc_id: str
):

    if not chunks:
        raise RuntimeError("NO_CHUNKS_TO_INGEST")

    path = get_index_path(course_id)
    os.makedirs(path, exist_ok=True)

    _ensure_index_meta(path, course_id)

    store_path = os.path.join(path, "docstore.json")
    vector_path = os.path.join(path, "faiss_index.json")

    existing = {}
    if os.path.exists(store_path):
        try:
            with open(store_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = {}

    new_chunks_added = 0
    total_tokens = 0
    empty_chunks = 0
    pages_seen = set()

    total_input_chunks = len(chunks)

    for c in chunks:

        if not c or not c.get("text"):
            empty_chunks += 1
            continue

        pages_seen.add(c.get("page", 0))

        clean_text = canonicalize_text(c["text"])

        if not clean_text:
            empty_chunks += 1
            continue

        uid = get_canonical_hash({
            "doc_id": doc_id,
            "text": clean_text,
            "page": c.get("page", 0),
        })

        if uid in existing:
            continue

        token_count = estimate_tokens(clean_text)
        total_tokens += token_count

        existing[uid] = {
            "text": clean_text,
            "metadata": {
                "course_id": course_id,
                "doc_id": doc_id,
                "file_name": filename,
                "page": c.get("page", 0),
                "index_version": INDEX_VERSION,
                "embedding_model_tag": EMBEDDING_MODEL_TAG,
                "estimated_tokens": token_count
            }
        }

        new_chunks_added += 1

    if new_chunks_added == 0:
        raise RuntimeError("ALL_CHUNKS_DUPLICATED_OR_EMPTY")

    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    # ensure vector index file exists (retrieval layer will use same folder)
    if not os.path.exists(vector_path):
        with open(vector_path, "w", encoding="utf-8") as f:
            json.dump({}, f)

    # =========================
    # INGESTION METRICS LOGGING
    # =========================

    avg_tokens = total_tokens / new_chunks_added if new_chunks_added else 0
    empty_ratio = empty_chunks / total_input_chunks if total_input_chunks else 0

    logger.info(
        f"""
[INGESTION REPORT]
Course: {course_id}
File: {filename}
Doc ID: {doc_id}
--------------------------------
total_pages: {len(pages_seen)}
total_input_chunks: {total_input_chunks}
total_new_chunks: {new_chunks_added}
avg_tokens_per_chunk: {round(avg_tokens, 2)}
empty_chunk_ratio: {round(empty_ratio, 3)}
"""
    )

    return {
        "status": "INGEST_OK",
        "new_chunks": new_chunks_added,
        "total_pages": len(pages_seen),
        "avg_tokens_per_chunk": round(avg_tokens, 2),
        "empty_chunk_ratio": round(empty_ratio, 3)
    }


def ingest_txt_only(text, course_id: str, filename: str, doc_id: str):

    if isinstance(text, list):
        chunks = text

    elif isinstance(text, str):
        chunks = [{
            "text": text,
            "page": 1
        }]

    else:
        raise TypeError("Unsupported text format for ingestion")

    return ingest_canonical_chunks(chunks, course_id, filename, doc_id)