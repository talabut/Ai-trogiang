from typing import List, Tuple, Dict
from langchain.schema import Document

from backend.vectorstore.faiss_store import get_faiss_store
from backend.vectorstore.bm25_store import BM25Store


FAISS_K = 5
BM25_K = 5

FAISS_WEIGHT = 0.6
BM25_WEIGHT = 0.4


def hybrid_search(query: str) -> List[Tuple[Document, float]]:
    """
    Hybrid retrieval: FAISS (semantic) + BM25 (keyword)
    Returns list of (Document, hybrid_score)
    """

    faiss_store = get_faiss_store()
    bm25_store = BM25Store.load()

    faiss_results = faiss_store.similarity_search_with_score(
        query,
        k=FAISS_K
    )

    bm25_results = bm25_store.search(
        query,
        k=BM25_K
    )

    score_map: Dict[str, Dict] = {}

    # --- FAISS results ---
    for doc, score in faiss_results:
        doc_key = f"{doc.metadata.get('doc_id')}:{doc.metadata.get('chunk_id')}"
        semantic_score = 1 / (1 + score)  # normalize distance → similarity

        score_map[doc_key] = {
            "doc": doc,
            "semantic": semantic_score,
            "keyword": 0.0
        }

    # --- BM25 results ---
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

    # --- Combine scores ---
    results: List[Tuple[Document, float]] = []

    for entry in score_map.values():
        hybrid_score = (
            FAISS_WEIGHT * entry["semantic"]
            + BM25_WEIGHT * entry["keyword"]
        )
        results.append((entry["doc"], hybrid_score))

    # Sort by hybrid score desc
    results.sort(key=lambda x: x[1], reverse=True)

    return results
