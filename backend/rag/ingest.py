import os
from backend.vectorstore.faiss_store import EMBEDDING_MODEL
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from backend.utils.text_extraction import extract_text
from backend.utils.chunking import chunk_text

def ingest_document(file_path: str, course_id: str):
    """
    Xử lý tài liệu: Trích xuất -> Chia nhỏ -> Chuyển thành Vector -> Lưu/Cập nhật FAISS
    """
    # 1. Trích xuất văn bản (Sửa lỗi: Hỗ trợ PDF, Docx, Txt thay vì chỉ TextLoader)
    try:
        text = extract_text(file_path)
        file_name = os.path.basename(file_path)
    except Exception as e:
        print(f"Lỗi khi trích xuất văn bản: {e}")
        raise e

    # 2. Chia nhỏ văn bản với đầy đủ Metadata (Sửa lỗi: Thiếu chunk_id cho module Evaluation)
    # Sử dụng chunk_text từ utils để đảm bảo metadata đồng nhất
    docs = chunk_text(text, source_file=file_name)

    # 3. Khởi tạo Embeddings model
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # Đường dẫn lưu index theo từng môn học
    index_path = os.path.join("data", "faiss_index", course_id)
    
    # 4. Kiểm tra và cập nhật Vector Store (Sửa lỗi: Upload file mới không làm mất dữ liệu file cũ)
    if os.path.exists(os.path.join(index_path, "index.faiss")):
        # Nếu đã có index, load lên và thêm tài liệu mới vào
        vector_store = FAISS.load_local(
            index_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        vector_store.add_documents(docs)
    else:
        # Nếu chưa có, tạo index mới từ danh sách docs
        vector_store = FAISS.from_documents(docs, embeddings)

    # 5. Lưu lại index cục bộ
    if not os.path.exists("data/faiss_index"):
        os.makedirs("data/faiss_index")
    
    vector_store.save_local(index_path)
    print(f"Đã ingest và cập nhật vector thành công cho môn {course_id}")