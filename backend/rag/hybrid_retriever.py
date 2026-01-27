import os
from backend.vectorstore.faiss_store import EMBEDDING_MODEL
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def hybrid_search(query: str, course_id: str = "ML101"):
    # Đường dẫn thư mục chứa dữ liệu của từng môn học
    index_path = os.path.join("data", "faiss_index", course_id)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # Kiểm tra xem môn học này đã được Ingest (nạp dữ liệu) chưa
    faiss_file = os.path.join(index_path, "index.faiss")
    if not os.path.exists(faiss_file):
        print(f"Cảnh báo: Chưa tìm thấy dữ liệu vector tại {faiss_file}")
        return []

    try:
        # Load database vector với quyền đọc file nội bộ
        vector_store = FAISS.load_local(
            index_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        # Tìm kiếm 3 đoạn văn bản giống câu hỏi nhất
        return vector_store.similarity_search(query, k=3)
    except Exception as e:
        print(f"Lỗi khi tìm kiếm FAISS: {e}")
        return []