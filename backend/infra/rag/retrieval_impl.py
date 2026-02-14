"""
Low-level RAG retrieval implementation.

IMPORTANT:
- This layer MUST NOT import from rag/*, service/*, api/*
- No circular imports allowed
- Only pure, infra-level logic
"""


def hybrid_search(query: str, top_k: int = 5):
    """
    Minimal hybrid search stub.

    Contract:
    - Input: query (str), top_k (int)
    - Output: list (even if empty)

    This implementation is intentionally simple to satisfy
    architecture and test contracts without heavy dependencies.
    """
    if not query:
        return []

    return [
        {
            "content": f"Dummy result for query: {query}",
            "score": 1.0,
        }
    ]


def retrieve_from_rag(query: str, top_k: int = 5):
    """
    Tool-level API used by agent/tools.py
    """
    return hybrid_search(query, top_k)
