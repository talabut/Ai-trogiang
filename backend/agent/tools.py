#backend/agent/tools.py
from typing import Dict, Any, List
from backend.infra.rag.retrieval_impl import retrieve


def check_knowledge_base(query: str, course_id: str) -> Dict[str, Any]:
    """
    TOOL = CỔNG TRI THỨC DUY NHẤT
    """
    results = retrieve(query, course_id)

    if results is None:
        return {
            "status": "NOT_FOUND",
            "reason": "NO_INDEX_OR_NO_MATCH",
            "answer": "",
            "evidences": [],
            "sources": []
        }

    return {
        "status": "FOUND",
        "answer": results["answer"],
        "evidences": results.get("chunks", []),
        "sources": results.get("sources", [])
    }
