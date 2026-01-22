import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

INDEX_DIR = "data/faiss_index"


def get_retriever():
    if not os.path.exists(INDEX_DIR):
        raise ValueError("Chưa ingest tài liệu. Hãy chạy ingest.py")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.load_local(
        INDEX_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return db.as_retriever(search_kwargs={"k": 3})
