# backend/api/chat.py

from fastapi import APIRouter

from backend.api.schemas import ChatRequest
from backend.services.agent import agent_service

router = APIRouter()


@router.post("/chat")
def chat(req: ChatRequest):
    result = agent_service.chat(
        question=req.question,
        session_id=req.session_id,
        course_id=req.course_id,
    )

    if result.get("answer") is None:
        return {
            "success": False,
            "reason": result.get("reason", "WEAK_EVIDENCE"),
            "message": result.get(
                "message",
                "Tài liệu có đề cập gián tiếp nhưng không đủ bằng chứng học thuật để trả lời.",
            ),
            "retrieval_stats": result.get(
                "retrieval_stats", {"nodes_found": 0, "max_score": 0.0}
            ),
        }

    return {
        "success": True,
        "data": {
            "answer": result["answer"],
            "evidence_count": len(result["evidences"]),
            "sources": result.get("sources", []),
            "ingest_status": "READY",
            "refusal": False,
            "reason": result.get("reason"),
            "retrieval_stats": result.get(
                "retrieval_stats", {"nodes_found": len(result["evidences"]), "max_score": 0.0}
            ),
        },
        "error": None,
    }
