from typing import List, Dict, Any
from backend.vectorstore.bm25_store import BM25Store
# FIX: Import retriever từ llama_ingest (nơi chứa logic load index)
from backend.rag.llama_ingest import get_llama_retriever

# Cấu hình cố định theo SPEC
THRESHOLD = 0.2
TOP_K_RETRIEVAL = 10
TOP_K_FINAL = 5

def normalize_scores(scores: List[float]) -> List[float]:
    """Min-Max Normalization to [0, 1] range."""
    if not scores: return []
    min_s, max_s = min(scores), max(scores)
    if max_s == min_s: return [1.0 for _ in scores] if max_s > 0 else [0.0 for _ in scores]
    return [(s - min_s) / (max_s - min_s) for s in scores]

def hybrid_search(query: str, course_id: str, k: int = TOP_K_FINAL) -> List[Dict[str, Any]]:
    """
    FIXED Hybrid Search: Vector (LlamaIndex) + BM25.
    Tuân thủ: Chunk Boundary Dedup, No Python hash(), Strict Metadata, Refusal Logic.
    """
    if not query or not query.strip():
        return []

    # 1. Vector Retrieval
    vector_retriever = get_llama_retriever(course_id, top_k=TOP_K_RETRIEVAL)
    vector_nodes = []
    if vector_retriever:
        try:
            vector_nodes = vector_retriever.retrieve(query)
        except Exception:
            vector_nodes = []

    # 2. BM25 Retrieval
    bm25_store = BM25Store.load(course_id)
    bm25_docs = []
    if bm25_store:
        bm25_docs = bm25_store.search(query, k=TOP_K_RETRIEVAL)

    # 3. Score Normalization
    v_scores = normalize_scores([n.score for n in vector_nodes])
    b_scores = normalize_scores([d.get("score", 0.0) for d in bm25_docs])

    # 4. Weighted Fusion & Strict Logic
    # Dùng dictionary để dedup theo CHUNK BOUNDARY
    fused_map = {}

    # Fusion rules: 0.6 Vector / 0.4 BM25
    
    # Process Vector Results
    for i, node in enumerate(vector_nodes):
        meta = node.metadata
        # 5. Metadata Validation (Drop if missing)
        required = ["doc_id", "page", "line_start", "line_end", "file_name"]
        if not all(meta.get(f) is not None for f in required):
            continue
            
        # 1. Dedup theo Chunk Boundary (No Python hash)
        chunk_id = f"{meta['doc_id']}_{meta['page']}_{meta['line_start']}_{meta['line_end']}"
        
        if chunk_id not in fused_map:
            # 4. Flatten Metadata Output Schema
            fused_map[chunk_id] = {
                "text": node.text,
                "doc_id": meta["doc_id"],
                "page": meta["page"],
                "line_start": meta["line_start"],
                "line_end": meta["line_end"],
                "file_name": meta["file_name"],
                "final_score": 0.0
            }
        fused_map[chunk_id]["final_score"] += v_scores[i] * 0.6

    # Process BM25 Results
    for i, doc in enumerate(bm25_docs):
        meta = doc.get("metadata", {})
        if not all(meta.get(f) is not None for f in required):
            continue
            
        chunk_id = f"{meta['doc_id']}_{meta['page']}_{meta['line_start']}_{meta['line_end']}"
        
        if chunk_id not in fused_map:
            fused_map[chunk_id] = {
                "text": doc.get("text", ""),
                "doc_id": meta["doc_id"],
                "page": meta["page"],
                "line_start": meta["line_start"],
                "line_end": meta["line_end"],
                "file_name": meta["file_name"],
                "final_score": 0.0
            }
        fused_map[chunk_id]["final_score"] += b_scores[i] * 0.4

    # 3. Refusal Logic (Threshold & Empty check)
    final_list = [
        res for res in fused_map.values() 
        if res["final_score"] >= THRESHOLD
    ]
    
    if not final_list:
        return []

    # Sort & Return top K
    final_list.sort(key=lambda x: x["final_score"], reverse=True)
    return final_list[:k]