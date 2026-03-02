# backend/api/chat.py

from fastapi import APIRouter
from backend.services.agent import agent_service
from backend.api.schemas import ChatRequest

router = APIRouter()

@router.post("/chat")
def chat(req: ChatRequest):
    result = agent_service.chat(
        question=req.question,
        session_id=req.session_id,
        course_id=req.course_id
    )

    # Handle NOT_FOUND or refusal case
    if result.get("answer") is None:
        return {
            "success": False,
            "data": None,
            "error": {
                "code": "NOT_FOUND",
                "message": result.get("reason", "No relevant information found.")
            }
        }

    return {
        "success": True,
        "data": {
            "answer": result["answer"],
            "evidence_count": len(result["evidences"]),
            "sources": result.get("sources", []),
            "ingest_status": "READY",
            "refusal": False,
            "reason": result.get("reason")
        },
        "error": None
    }