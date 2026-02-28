import json
import os
import shutil
from datetime import datetime

from backend.rag.llama_ingest import (
    INDEX_VERSION,
    EMBEDDING_MODEL_TAG,
)

META_FILENAME = "index_meta.json"


def expected_meta(course_id: str):
    """
    🔥 Single Source of Truth cho metadata index.
    Phải đồng bộ với llama_ingest + retrieval layer.
    """
    return {
        "course_id": course_id,
        "index_version": INDEX_VERSION,
        "embedding_model_tag": EMBEDDING_MODEL_TAG,
        "timestamp": datetime.utcnow().isoformat()
    }


def write_meta(index_dir: str, course_id: str):
    os.makedirs(index_dir, exist_ok=True)

    meta_path = os.path.join(index_dir, META_FILENAME)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(
            expected_meta(course_id),
            f,
            indent=2,
            ensure_ascii=False,
            sort_keys=True
        )


def clear_index(index_dir: str):
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)


def assert_meta_compatible(index_dir: str, course_id: str):
    """
    🔥 Fail fast nếu metadata mismatch.
    """
    path = os.path.join(index_dir, META_FILENAME)

    if not os.path.exists(path):
        raise RuntimeError("INDEX_META_MISSING")

    with open(path, "r", encoding="utf-8") as f:
        stored = json.load(f)

    current = expected_meta(course_id)

    # không so timestamp
    stored_compare = {
        k: v for k, v in stored.items()
        if k != "timestamp"
    }

    current_compare = {
        k: v for k, v in current.items()
        if k != "timestamp"
    }

    if stored_compare != current_compare:
        raise RuntimeError("INDEX_META_MISMATCH")