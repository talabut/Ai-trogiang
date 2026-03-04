# backend/agent/tools.py
from typing import Dict, Any, List

from llama_index.core.schema import NodeWithScore

from backend.infra.rag.retrieval_impl import retrieve


def check_knowledge_base(query: str, course_id: str) -> Dict[str, Any]:
    """
    TOOL = cong tri thuc duy nhat
    """

    results: List[NodeWithScore] = retrieve(query, course_id)

    if not results:
        return {
            "status": "NOT_FOUND",
            "reason": "NO_INDEX_OR_NO_MATCH",
            "answer": "",
            "evidences": [],
            "sources": [],
            "retrieval_stats": {
                "nodes_found": 0,
                "max_score": 0.0,
            },
        }

    evidences = []
    sources = []

    for node in results:
        text = node.node.get_content()
        score = node.score
        metadata = node.node.metadata or {}

        evidences.append(
            {
                "text": text,
                "score": float(score) if score is not None else None,
                "metadata": metadata,
            }
        )

        source_name = metadata.get("source") or metadata.get("file_name")
        if source_name:
            sources.append(source_name)

    max_score = max(
        (ev["score"] for ev in evidences if ev.get("score") is not None),
        default=0.0,
    )

    return {
        "status": "FOUND",
        "answer": "",  # generation layer se xu ly sau
        "evidences": evidences,
        "sources": list(set(sources)),
        "retrieval_stats": {
            "nodes_found": len(evidences),
            "max_score": float(max_score),
        },
    }
