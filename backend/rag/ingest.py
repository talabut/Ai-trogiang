# backend/rag/ingest.py

from typing import List
from backend.vectorstore.faiss_store import get_faiss_store

def ingest_document(
    texts: List[str],
    metadatas: List[dict]
):
    if not texts:
        raise ValueError("No extracted text to ingest")

    if len(texts) != len(metadatas):
        raise ValueError("texts and metadatas length mismatch")

    faiss_store = get_faiss_store()

    faiss_store.add_texts(
        texts=texts,
        metadatas=metadatas
    )

    return {
        "status": "success",
        "chunks": len(texts)
    }
