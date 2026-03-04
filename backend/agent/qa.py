# backend/agent/qa.py
from typing import Dict, Any


class QAAgent:
    """
    QAAgent:
    - Khong generate
    - Khong build prompt
    - Chi kiem tra retrieval result
    """

    def answer(
        self,
        question: str,
        tool_result: Dict[str, Any],
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
                "reason": "NO_MATCH",
                "evidences": [],
                "sources": [],
                "retrieval_stats": tool_result.get(
                    "retrieval_stats", {"nodes_found": 0, "max_score": 0.0}
                ),
            }

        return {
            "answer": None,
            "confidence": 0.5,
            "reason": "EVIDENCE_FOUND",
            "evidences": evidences,
            "sources": tool_result.get("sources", []),
            "retrieval_stats": tool_result.get(
                "retrieval_stats",
                {
                    "nodes_found": len(evidences),
                    "max_score": max(
                        (ev.get("score") or 0.0 for ev in evidences), default=0.0
                    ),
                },
            ),
        }
