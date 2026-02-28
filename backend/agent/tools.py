# backend/agent/tools.py
from typing import Dict, Any, List
from backend.infra.rag.retrieval_impl import retrieve
from llama_index.core.schema import NodeWithScore


def check_knowledge_base(query: str, course_id: str) -> Dict[str, Any]:
    """
    TOOL = CỔNG TRI THỨC DUY NHẤT
    """

    results: List[NodeWithScore] = retrieve(query, course_id)

    if not results:
        return {
            "status": "NOT_FOUND",
            "reason": "NO_INDEX_OR_NO_MATCH",
            "answer": "",
            "evidences": [],
            "sources": []
        }

    evidences = []
    sources = []

    for node in results:
        text = node.node.get_content()
        score = node.score
        metadata = node.node.metadata or {}

        evidences.append({
            "text": text,
            "score": float(score) if score is not None else None,
            "metadata": metadata
        })

        if metadata.get("source"):
            sources.append(metadata.get("source"))

    return {
        "status": "FOUND",
        "answer": "",  # Generation layer sẽ xử lý sau
        "evidences": evidences,
        "sources": list(set(sources))
    }