import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Sử dụng model nhỏ để tiết kiệm RAM
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Khởi tạo singleton để dùng chung toàn hệ thống, tránh tốn RAM [cite: 99]
embeddings_instance = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def get_faiss_store(index_path: str):
    """
    Load FAISS store từ đĩa nếu tồn tại, nếu không trả về None [cite: 99]
    """
    if os.path.exists(os.path.join(index_path, "index.faiss")):
        return FAISS.load_local(
            index_path, 
            embeddings_instance, 
            allow_dangerous_deserialization=True
        )
    return None