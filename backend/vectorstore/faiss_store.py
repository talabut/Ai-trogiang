# backend/vectorstore/faiss_store.py

import os
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

_FAISS_STORE = None
FAISS_PATH = "data/faiss_index"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_faiss_store():
    global _FAISS_STORE

    if _FAISS_STORE is not None:
        return _FAISS_STORE

    embeddings = get_embeddings()

    index_file = os.path.join(FAISS_PATH, "index.faiss")

    if os.path.exists(index_file):
        # ✅ Load index cũ
        _FAISS_STORE = FAISS.load_local(
            FAISS_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        # ✅ Tạo index mới (EMPTY, không crash)
        _FAISS_STORE = FAISS.from_texts(
            texts=["__init__"],
            embedding=embeddings,
            metadatas=[{"system": True}]
        )

        os.makedirs(FAISS_PATH, exist_ok=True)
        _FAISS_STORE.save_local(FAISS_PATH)

    return _FAISS_STORE


def save_faiss_store():
    if _FAISS_STORE is not None:
        _FAISS_STORE.save_local(FAISS_PATH)
