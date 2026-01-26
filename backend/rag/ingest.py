import os
# Cập nhật đường dẫn import mới
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter 
from backend.vectorstore.faiss_store import get_faiss_store

def ingest_document(file_path: str, course_id: str):
    # 1. Load document
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()

    # 2. Chia nhỏ văn bản (Sử dụng class từ langchain_text_splitters)
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    # 3. Gán metadata
    for d in docs:
        d.metadata["course_id"] = course_id
        d.metadata["source_file"] = os.path.basename(file_path)

    # 4. Thêm vào Vector Store
    vector_store = get_faiss_store()
    vector_store.add_documents(docs)
    
    # 5. Lưu index xuống ổ đĩa
    index_dir = "data/faiss_index"
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
        
    index_path = os.path.join(index_dir, course_id)
    vector_store.save_local(index_path)
    print(f"--- Đã Ingest xong khóa học: {course_id} ---")