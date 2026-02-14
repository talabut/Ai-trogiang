from fastapi import APIRouter
from backend.services.agent import agent_service
from backend.api.schemas import ChatRequest

router = APIRouter()

@router.post("/chat")
def chat(request: ChatRequest):
    answer = agent_service.chat(
        question=request.question,
        session_id=request.session_id,
    )

    return {
        "success": True,
        "data": {
            "answer": answer,
            "evidence_count": 0,
            "sources": [],
            "ingest_status": "READY",
            "refusal": False,
        }
    }
