from backend.rag.chunking import ingest_with_lock
from backend.vectorstore.faiss_store import persist_faiss_index

def llama_ingest(text: str):
    def _do_ingest(t: str):
        # assume vectorization already done upstream
        persist_faiss_index()

    return ingest_with_lock(text, _do_ingest)
