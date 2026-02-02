# backend/vectorstore/atomic_persist.py
import os
import shutil
import tempfile

from backend.vectorstore.index_meta import write_meta


def atomic_persist(index_dir: str, persist_fn):
    parent = os.path.dirname(index_dir.rstrip("/")) or "."
    tmp_dir = tempfile.mkdtemp(prefix="faiss_tmp_", dir=parent)

    try:
        persist_fn(tmp_dir)
        write_meta(tmp_dir)

        if os.path.exists(index_dir):
            shutil.rmtree(index_dir)

        os.rename(tmp_dir, index_dir)
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
