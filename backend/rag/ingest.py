from backend.utils.chunking import chunk_text
from backend.vectorstore.faiss_store import get_faiss_store, save_faiss_store
from backend.vectorstore.bm25_store import BM25Store


def ingest_document(raw_text: str, source_file: str):
    if not raw_text or len(raw_text.strip()) < 50:
        raise ValueError("Extracted text is empty or too short.")

    documents = chunk_text(
        text=raw_text,
        source_file=source_file
    )

    faiss_store = get_faiss_store()
    faiss_store.add_documents(documents)
    save_faiss_store()

    bm25_store = BM25Store.load()
    bm25_store.add_documents(documents)
    bm25_store.save()

    return {
        "status": "success",
        "chunks": len(documents),
        "source_file": source_file
    }
