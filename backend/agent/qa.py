# backend/agent/qa.py
from typing import Dict, Any


class QAAgent:
    """
    QAAgent:
    - KHÔNG generate
    - KHÔNG build prompt
    - Chỉ kiểm tra retrieval result
    """

    def answer(
        self,
        question: str,
        tool_result: Dict[str, Any]
    ) -> Dict[str, Any]:

        if tool_result is None:
            raise RuntimeError(
                "QAAgent: tool_result is REQUIRED. Agent cannot answer without tool."
            )

        status = tool_result.get("status")
        evidences = tool_result.get("evidences", [])

        if status != "FOUND" or not evidences:
            return {
                "answer": None,
                "confidence": 0.0,
                "reason": "NOT_FOUND_IN_DATABASE",
                "evidences": [],
                "sources": []
            }

        return {
            "answer": None,  # LLM sẽ fill sau
            "confidence": 0.5,
            "reason": "EVIDENCE_FOUND",
            "evidences": evidences,
            "sources": tool_result.get("sources", [])
        }