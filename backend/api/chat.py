# backend/api/chat.py

from fastapi import APIRouter
from backend.agent.qa import answer_question

router = APIRouter()

@router.post("/chat")
def chat(query: str):
    """
    Chat endpoint with threshold + refusal
    """
    return answer_question(query)
