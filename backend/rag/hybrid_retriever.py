from backend.vectorstore.faiss_store import get_faiss_store
from backend.vectorstore.bm25_store import BM25Store
import os

def hybrid_search(query: str, course_id: str, k: int = 5):
    if not query or len(query.strip()) < 2:
        return []

    # FIX: Đường dẫn phải khớp với logic trong ingest.py
    index_path = os.path.join("data", "faiss_index", course_id)
    
    vector_store = get_faiss_store(index_path)
    bm25_store = BM25Store.load(course_id)

    vector_results = []
    if vector_store:
        # Trả về Document và score
        vector_results = vector_store.similarity_search_with_score(query, k=k)

    bm25_results = []
    if bm25_store:
        bm25_results = bm25_store.search(query, k=k)

    combined = []
    # Chuẩn hóa format kết quả trả về cho Frontend và Agent
    for doc, score in vector_results:
        combined.append({
            "content": doc.page_content, 
            "source_file": doc.metadata.get("source_file", "Unknown"),
            "page": doc.metadata.get("page"),
            "section": doc.metadata.get("section"),
            "chunk_id": doc.metadata.get("chunk_id"),
            "score": float(score),
            "type": "vector"
        })
    
    for doc, score in bm25_results:
        combined.append({
            "content": doc.page_content, 
            "source_file": doc.metadata.get("source_file", "Unknown"),
            "page": doc.metadata.get("page"),
            "section": doc.metadata.get("section"),
            "chunk_id": doc.metadata.get("chunk_id"),
            "score": float(score),
            "type": "bm25"
        })

    # Sắp xếp theo score và lấy k kết quả đầu tiên
    return combined[:k]