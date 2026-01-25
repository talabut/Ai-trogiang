from typing import List, Tuple, Dict
from langchain_core.documents import Document

from backend.vectorstore.faiss_store import get_faiss_store
from backend.vectorstore.bm25_store import BM25Store


FAISS_K = 5
BM25_K = 5

FAISS_WEIGHT = 0.6
BM25_WEIGHT = 0.4

MIN_QUERY_LENGTH = 5


def hybrid_search(query: str) -> List[Tuple[Document, float]]:
    """
    Hybrid retrieval: FAISS (semantic) + BM25 (keyword)

    Defensive rules:
    - Reject empty / too-short query
    - Safe when FAISS/BM25 are empty (cold-start)
    - Never throw exception
    """

    # === INPUT VALIDATION ===
    if not query or not isinstance(query, str):
        return []

    query = query.strip()
    if len(query) < MIN_QUERY_LENGTH:
        return []

    # === LOAD STORES (COLD-START SAFE) ===
    try:
        faiss_store = get_faiss_store()
    except Exception:
        faiss_store = None

    try:
        bm25_store = BM25Store.load()
    except Exception:
        bm25_store = None

    score_map: Dict[str, Dict] = {}

    # === FAISS SEARCH ===
    if faiss_store is not None:
        try:
            faiss_results = faiss_store.similarity_search_with_score(
                query,
                k=FAISS_K
            )
        except Exception:
            faiss_results = []

        for doc, score in faiss_results:
            doc_key = f"{doc.metadata.get('doc_id')}:{doc.metadata.get('chunk_id')}"
            semantic_score = 1 / (1 + score)  # distance → similarity

            score_map[doc_key] = {
                "doc": doc,
                "semantic": semantic_score,
                "keyword": 0.0
            }

    # === BM25 SEARCH ===
    if bm25_store is not None:
        try:
            bm25_results = bm25_store.search(query, k=BM25_K)
        except Exception:
            bm25_results = []

        for doc, score in bm25_results:
            doc_key = f"{doc.metadata.get('doc_id')}:{doc.metadata.get('chunk_id')}"

            if doc_key not in score_map:
                score_map[doc_key] = {
                    "doc": doc,
                    "semantic": 0.0,
                    "keyword": score
                }
            else:
                score_map[doc_key]["keyword"] = score

    # === COMBINE SCORES ===
    results: List[Tuple[Document, float]] = []

    for entry in score_map.values():
        hybrid_score = (
            FAISS_WEIGHT * entry["semantic"]
            + BM25_WEIGHT * entry["keyword"]
        )

        if hybrid_score > 0:
            results.append((entry["doc"], hybrid_score))

    results.sort(key=lambda x: x[1], reverse=True)

    return results
