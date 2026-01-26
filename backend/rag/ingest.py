import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from backend.vectorstore.faiss_store import EMBEDDING_MODEL
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def ingest_document(file_path: str, course_id: str):
    # 1. Load file
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()

    # 2. Chia nhỏ văn bản
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    # 3. Chuyển thành Vector và lưu
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = FAISS.from_documents(docs, embeddings)
    
    index_path = f"data/faiss_index/{course_id}"
    if not os.path.exists("data/faiss_index"):
        os.makedirs("data/faiss_index")
        
    vector_store.save_local(index_path)