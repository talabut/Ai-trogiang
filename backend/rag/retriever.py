from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import os

BASE_INDEX_DIR = "data/faiss_index"

def get_retriever(course_id: str):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    index_path = os.path.join(BASE_INDEX_DIR, course_id)

    if not os.path.exists(index_path):
        raise ValueError("Course chưa có dữ liệu")

    db = FAISS.load_local(index_path, embeddings)
    return db.as_retriever()
