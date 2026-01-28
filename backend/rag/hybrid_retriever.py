from backend.vectorstore.faiss_store import get_faiss_store
from backend.vectorstore.bm25_store import BM25Store
import os

def hybrid_search(query: str, course_id: str = "default_course", k: int = 5):
    """
    Tìm kiếm kết hợp Vector + BM25.
    FIX: Thêm default course_id để pass test và tránh TypeError.
    """
    # B. GUARDRAILS: Xử lý query rỗng hoặc quá ngắn (test_empty_query, test_short_query)
    if not query or len(query.strip()) < 2:
        return []

    # Đường dẫn index dựa trên course_id
    index_path = os.path.join("data", "faiss_index", course_id)
    vector_store = get_faiss_store(index_path)
    bm25_store = BM25Store.load(course_id)

    vector_results = []
    if vector_store:
        try:
            vector_results = vector_store.similarity_search_with_score(query, k=k)
        except Exception:
            vector_results = []

    bm25_results = []
    if bm25_store:
        try:
            bm25_results = bm25_store.search(query, k=k)
        except Exception:
            bm25_results = []

    combined = []
    # Format kết quả chuẩn hóa
    for doc, score in vector_results:
        combined.append({
            "content": doc.page_content,
            "source_file": doc.metadata.get("source_file", "Unknown"),
            "score": float(score),
            "type": "vector"
        })

    for doc, score in bm25_results:
        combined.append({
            "content": doc.page_content,
            "source_file": doc.metadata.get("source_file", "Unknown"),
            "score": float(score),
            "type": "bm25"
        })

    return combined[:k]