import os
from backend.vectorstore.faiss_store import embeddings_instance
from langchain_community.vectorstores import FAISS
from backend.utils.text_extraction import extract_text
from backend.utils.chunking import chunk_text
from backend.vectorstore.bm25_store import BM25Store

def ingest_document(file_path: str, course_id: str):
    # 1. Trích xuất văn bản
    text = extract_text(file_path)
    file_name = os.path.basename(file_path)

    # 2. Chia nhỏ văn bản (Sử dụng utils để có metadata chuẩn cho Eval) [cite: 78, 79]
    docs = chunk_text(text, source_file=file_name)

    # 3. Xử lý Vector Store (FAISS)
    index_path = os.path.join("data", "faiss_index", course_id)
    
    if os.path.exists(os.path.join(index_path, "index.faiss")):
        vector_store = FAISS.load_local(
            index_path, 
            embeddings_instance, 
            allow_dangerous_deserialization=True
        )
        vector_store.add_documents(docs)
    else:
        vector_store = FAISS.from_documents(docs, embeddings_instance)

    if not os.path.exists(os.path.dirname(index_path)):
        os.makedirs(os.path.dirname(index_path))
    
    vector_store.save_local(index_path)

    # 4. Xử lý Keyword Store (BM25) - Quan trọng để hybrid_search không lỗi [cite: 85, 87]
    bm25_store = BM25Store.load(course_id)
    bm25_store.add_documents(docs)
    bm25_store.save()

    print(f"Thành công: Đã cập nhật FAISS và BM25 cho môn {course_id}")