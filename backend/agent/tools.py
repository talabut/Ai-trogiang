from typing import Dict, Any, List
from backend.infra.rag.retrieval_impl import retrieve_from_rag


def check_knowledge_base(query: str) -> Dict[str, Any]:
    """
    TOOL = CỔNG TRI THỨC DUY NHẤT
    """

    results = retrieve_from_rag(query)

    if not results:
        return {
            "status": "NOT_FOUND",
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
