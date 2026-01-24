from backend.utils.chunking import chunk_text
from backend.vectorstore.faiss_store import get_faiss_store
from backend.vectorstore.bm25_store import BM25Store


def ingest_document(
    raw_text: str,
    source_file: str,
    page: int = None,
    section: str = None
):
    """
    Ingest document into FAISS + BM25 (Hybrid ready)
    """

    documents = chunk_text(
        text=raw_text,
        source_file=source_file,
        page=page,
        section=section
    )

    # === FAISS (semantic search) ===
    faiss_store = get_faiss_store()
    faiss_store.add_documents(documents)
    faiss_store.save_local("data/faiss_index")

    # === BM25 (keyword search) ===
    bm25_store = BM25Store.load()
    bm25_store.add_documents(documents)
    bm25_store.save()

    return {
        "status": "success",
        "chunks": len(documents),
        "source_file": source_file
    }
