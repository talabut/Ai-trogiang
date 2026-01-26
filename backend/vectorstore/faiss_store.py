import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Sử dụng model nhỏ để tiết kiệm RAM và chạy nhanh trên CPU
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def get_faiss_store():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    # Khởi tạo một store trống để tránh lỗi 500 khi chưa có dữ liệu
    return FAISS.from_texts(["Khởi tạo"], embeddings)