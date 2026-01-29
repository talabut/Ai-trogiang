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

    # 2. Chia nhỏ văn bản
    docs = chunk_text(text, source_file=file_name)

    # 3. FAISS
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

    os.makedirs(index_path, exist_ok=True)
    vector_store.save_local(index_path)

    # 4. BM25
    bm25_store = BM25Store.load(course_id)
    bm25_store.add_documents(docs)
    bm25_store.save()

    print(f"✅ Ingest xong cho course {course_id}")
