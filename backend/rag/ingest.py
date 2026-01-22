import os
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

RAW_DIR = "data/raw_docs"
INDEX_DIR = "data/faiss_index"


def load_documents():
    documents = []

    for file in os.listdir(RAW_DIR):
        path = os.path.join(RAW_DIR, file)

        if file.endswith(".txt"):
            loader = TextLoader(path, encoding="utf-8")
        elif file.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif file.endswith(".docx"):
            loader = Docx2txtLoader(path)
        else:
            continue

        documents.extend(loader.load())

    return documents


def ingest():
    docs = load_documents()
    if not docs:
        raise ValueError("Không có tài liệu nào trong data/raw_docs")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_DIR)

    print("✅ Ingest hoàn tất – FAISS index đã được tạo")


if __name__ == "__main__":
    ingest()
