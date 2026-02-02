import os
import faiss
import pickle
from backend.config.integrity_config import settings
from backend.vectorstore.atomic_persist import atomic_persist
from backend.vectorstore.index_meta import assert_meta_compatible

INDEX_FILE = "index.faiss"
STORE_FILE = "index.pkl"

def load_index():
    if os.path.exists(settings.FAISS_INDEX_DIR) and os.listdir(settings.FAISS_INDEX_DIR):
        assert_meta_compatible(settings.FAISS_INDEX_DIR)

    path = os.path.join(settings.FAISS_INDEX_DIR, INDEX_FILE)
    if not os.path.exists(path):
        raise RuntimeError("FAISS_INDEX_NOT_FOUND")

    return faiss.read_index(path)

def persist_faiss_index(index, store):
    def _persist(tmp_dir):
        faiss.write_index(index, os.path.join(tmp_dir, INDEX_FILE))
        with open(os.path.join(tmp_dir, STORE_FILE), "wb") as f:
            pickle.dump(store, f)

    atomic_persist(settings.FAISS_INDEX_DIR, _persist)
