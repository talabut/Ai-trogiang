from fastapi import APIRouter
from pydantic import BaseModel

from backend.agent.tutor_agent import get_tutor_agent

router = APIRouter()

class ChatRequest(BaseModel):
    question: str


@router.post("/")
def chat(req: ChatRequest):
    chain = get_tutor_agent()

    result = chain.invoke(req.question)

    if not result or len(result.strip()) == 0:
        return {"answer": "Không tìm thấy tài liệu phù hợp"}

    return {"answer": result}
