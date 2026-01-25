from backend.rag.hybrid_retriever import hybrid_search

MIN_RETRIEVAL_SCORE = 0.15

def evaluate_sample(sample: dict) -> dict:
    """
    sample = {
        id: int,
        question: str
    }
    """

    question = sample.get("question")
    if not question:
        raise ValueError("Missing question in eval sample")

    results = hybrid_search(question)

    grounded = False
    used_chunks = []

    for doc, score in results:
        if score >= MIN_RETRIEVAL_SCORE:
            grounded = True
            used_chunks.append({
                "chunk_id": doc.metadata.get("chunk_id"),
                "source_file": doc.metadata.get("source_file"),
                "score": round(score, 4)
            })

    return {
        "id": sample.get("id"),
        "question": question,
        "grounded": grounded,
        "num_chunks": len(used_chunks),
        "chunks": used_chunks,
        "score": 1.0 if grounded else 0.0
    }
