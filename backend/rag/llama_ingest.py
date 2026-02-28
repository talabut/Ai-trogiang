# FILE: backend/rag/llama_ingest.py

import os
import json
import logging
from typing import List, Dict, Any

from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from backend.rag.canonicalize import canonicalize_text, get_canonical_hash
from backend.config.integrity_config import settings

INDEX_VERSION = "v1.0"
EMBEDDING_MODEL_TAG = "sentence-transformers/all-MiniLM-L6-v2"

logger = logging.getLogger(__name__)


# =====================================================
# Helpers
# =====================================================

def get_index_path(course_id: str) -> str:
    return os.path.join(settings.FAISS_INDEX_DIR, course_id)


def _ensure_index_meta(path: str, course_id: str):
    meta_path = os.path.join(path, "index_meta.json")

    meta = {
        "course_id": course_id,
        "index_version": INDEX_VERSION,
        "embedding_model_tag": EMBEDDING_MODEL_TAG
    }

    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

        if (
            existing.get("index_version") != INDEX_VERSION
            or existing.get("embedding_model_tag") != EMBEDDING_MODEL_TAG
        ):
            raise RuntimeError("INDEX_META_MISMATCH")

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# =====================================================
# Main Ingestion
# =====================================================

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

    documents: List[Document] = []

    for c in chunks:

        if not c or not c.get("text"):
            continue

        clean_text = canonicalize_text(c["text"])

        if not clean_text:
            continue

        uid = get_canonical_hash({
            "doc_id": doc_id,
            "text": clean_text,
            "page": c.get("page", 0),
        })

        documents.append(
            Document(
                text=clean_text,
                doc_id=uid,
                metadata={
                    "course_id": course_id,
                    "doc_id": doc_id,
                    "file_name": filename,
                    "page": c.get("page", 0),
                    "index_version": INDEX_VERSION,
                    "embedding_model_tag": EMBEDDING_MODEL_TAG,
                }
            )
        )

    if not documents:
        raise RuntimeError("NO_VALID_DOCUMENTS")

    # =========================================
    # Build embedding model
    # =========================================

    embed_model = HuggingFaceEmbedding(
        model_name=EMBEDDING_MODEL_TAG
    )

    # =========================================
    # Create or load existing index
    # =========================================

    if os.listdir(path):
        try:
            storage_context = StorageContext.from_defaults(
                persist_dir=path
            )
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                embed_model=embed_model,
                show_progress=True
            )
        except Exception:
            index = VectorStoreIndex.from_documents(
                documents,
                embed_model=embed_model,
                show_progress=True
            )
    else:
        index = VectorStoreIndex.from_documents(
            documents,
            embed_model=embed_model,
            show_progress=True
        )

    # Persist
    index.storage_context.persist(persist_dir=path)

    logger.info(
        f"[INGEST_OK] course_id={course_id} | "
        f"new_chunks={len(documents)} | file={filename}"
    )

    return {
        "status": "INGEST_OK",
        "new_chunks": len(documents),
        "total_pages": len(set(d.metadata["page"] for d in documents))
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