import json
import os
from backend.rag.node_parser import (
    INGEST_VERSION,
    EMBEDDING_MODEL_TAG,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

META_FILENAME = "index.meta.json"

def expected_meta():
    return {
        "ingest_version": INGEST_VERSION,
        "embedding_model": EMBEDDING_MODEL_TAG,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
    }

def write_meta(index_dir):
    with open(os.path.join(index_dir, META_FILENAME), "w") as f:
        json.dump(expected_meta(), f, indent=2, sort_keys=True)

def assert_meta_compatible(index_dir):
    path = os.path.join(index_dir, META_FILENAME)
    if not os.path.exists(path):
        raise RuntimeError("INDEX_META_MISSING")

    with open(path) as f:
        stored = json.load(f)

    if stored != expected_meta():
        raise RuntimeError("INDEX_META_MISMATCH")
