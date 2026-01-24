from fastapi import APIRouter
from pydantic import BaseModel
from backend.agent.qa import answer_question
from backend.logging.audit import audit_log

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(req: ChatRequest):
    result = answer_question(req.question)

    audit_log(
        user="anonymous",   # có thể thay bằng user thật sau
        action="chat",
        payload={
            "question": req.question,
            "answer": result.get("answer"),
            "sources": result.get("sources"),
        }
    )

    return result
