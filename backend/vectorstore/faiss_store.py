from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

_INDEX_PATH = Path("data/faiss_index")
_faiss_store = None

def get_faiss_store():
    global _faiss_store

    if _faiss_store is not None:
        return _faiss_store

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if _INDEX_PATH.exists():
        _faiss_store = FAISS.load_local(
            _INDEX_PATH.as_posix(),
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        # cold start: index rỗng, KHÔNG crash
        _faiss_store = FAISS.from_texts(
            texts=[],
            embedding=embeddings
        )

    return _faiss_store


def save_faiss_store():
    if _faiss_store is not None:
        _INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        _faiss_store.save_local(_INDEX_PATH.as_posix())
