from typing import Dict, Any


class QAAgent:
    """
    QAAgent KHÔNG tạo tri thức.
    Nó chỉ:
    - Nhận tool_result
    - Kiểm tra trạng thái
    - Pass-through hoặc từ chối
    """

    def answer(self, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        if tool_result is None:
            raise RuntimeError("QAAgent: tool_result is REQUIRED. Agent cannot answer without tool.")

        status = tool_result.get("status")
        if status != "FOUND":
            return {
                "answer": None,
                "confidence": 0.0,
                "reason": "NOT_FOUND_IN_DATABASE",
                "evidences": [],
                "sources": []
            }

        # TUYỆT ĐỐI không synthesize
        return {
            "answer": tool_result.get("answer"),
            "confidence": 1.0,
            "reason": "FROM_DATABASE",
            "evidences": tool_result.get("evidences", []),
            "sources": tool_result.get("sources", [])
        }
