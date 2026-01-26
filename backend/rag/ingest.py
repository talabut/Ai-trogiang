import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from backend.vectorstore.faiss_store import get_faiss_store

def ingest_document(file_path: str, course_id: str):
    # 1. Load document
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()

    # 2. Chia nhỏ văn bản
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    # 3. Gán course_id vào metadata để sau này filter
    for d in docs:
        d.metadata["course_id"] = course_id

    # 4. Lưu vào FAISS
    vector_store = get_faiss_store()
    vector_store.add_documents(docs)
    
    # 5. Lưu xuống ổ đĩa
    index_path = f"data/faiss_index/{course_id}"
    if not os.path.exists("data/faiss_index"):
        os.makedirs("data/faiss_index")
    vector_store.save_local(index_path)