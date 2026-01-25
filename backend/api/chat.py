from fastapi import APIRouter
from backend.agent.qa import answer_question

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post(
    "/",
    operation_id="chat_answer_question"
)
def chat(question: str):
    return answer_question(question)
