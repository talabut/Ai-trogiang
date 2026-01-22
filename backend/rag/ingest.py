from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

import os

DATA_PATH = "data/raw_docs"
INDEX_PATH = "data/faiss_index"


def ingest_docs():
    documents = []

    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(DATA_PATH, filename), encoding="utf-8")
            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.from_documents(docs, embeddings)
    db.save_local(INDEX_PATH)


if __name__ == "__main__":
    ingest_docs()
