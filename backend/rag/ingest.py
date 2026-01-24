# backend/agent/ingest.py

from backend.utils.chunking import chunk_text
from backend.vectorstore.faiss_store import get_faiss_store

def ingest_document(
    raw_text: str,
    source_file: str,
    page: int = None,
    section: str = None
):
    """
    Ingest document into FAISS with proper chunking + metadata
    """

    documents = chunk_text(
        text=raw_text,
        source_file=source_file,
        page=page,
        section=section
    )

    vectorstore = get_faiss_store()

    vectorstore.add_documents(documents)

    vectorstore.save_local("data/faiss_index")

    return {
        "status": "success",
        "chunks": len(documents),
        "source_file": source_file
    }
