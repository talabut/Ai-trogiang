import os
from backend.vectorstore.faiss_store import EMBEDDING_MODEL
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def hybrid_search(query: str, course_id: str = "ML101"):
    index_path = os.path.join("data", "faiss_index", course_id)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # Kiểm tra file index tồn tại
    faiss_file = os.path.join(index_path, "index.faiss")
    if not os.path.exists(faiss_file):
        print(f"--- Warning: Không tìm thấy index tại {faiss_file} ---")
        return []

    try:
        vector_store = FAISS.load_local(
            index_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        return vector_store.similarity_search(query, k=3)
    except Exception as e:
        print(f"--- Lỗi FAISS Search: {e} ---")
        return []