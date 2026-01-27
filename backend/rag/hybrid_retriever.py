import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from backend.vectorstore.faiss_store import EMBEDDING_MODEL
from backend.vectorstore.bm25_store import BM25Store

def hybrid_search(query: str, course_id: str, k: int = 4):
    """
    Kết hợp kết quả từ Vector Search (FAISS) và Keyword Search (BM25).
    """
    if not query or len(query.strip()) < 2:
        return []

    index_path = os.path.join("data", "faiss_index", course_id)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # 1. Lấy kết quả từ Vector Search (FAISS)
    vector_docs = []
    if os.path.exists(os.path.join(index_path, "index.faiss")):
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        vector_docs = vector_store.similarity_search(query, k=k)

    # 2. Lấy kết quả từ Keyword Search (BM25)
    # Giả định BM25Store đã được lưu trong quá trình ingest
    bm25_docs = []
    bm25_store = BM25Store(course_id=course_id)
    try:
        bm25_store.load()
        bm25_docs = bm25_store.search(query, k=k)
    except:
        # Nếu chưa có index BM25 thì bỏ qua
        pass

    # 3. Kết hợp và loại bỏ trùng lặp (Simple Reranking)
    all_docs = vector_docs + bm25_docs
    unique_docs = []
    seen_content = set()

    for doc in all_docs:
        if doc.page_content not in seen_content:
            unique_docs.append(doc)
            seen_content.add(doc.page_content)

    return unique_docs[:k]