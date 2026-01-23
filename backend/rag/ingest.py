from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
import os

BASE_INDEX_DIR = "data/faiss_index"

def ingest_document(file_path: str, course_id: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    course_dir = os.path.join(BASE_INDEX_DIR, course_id)
    os.makedirs(course_dir, exist_ok=True)

    db = FAISS.from_documents(docs, embeddings)
    db.save_local(course_dir)
