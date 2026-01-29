# FILE: backend/api/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agent.qa import answer_question

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    course_id: str = "ML101"  # Default value để tránh lỗi nếu thiếu

# SỬA: Đổi path thành "/query" để khớp với prefix "/chat" ở main.py
# URL thực tế sẽ là: POST http://localhost:8000/chat/query
@router.post("/query")
async def chat_query(request: ChatRequest):
    try:
        # Gọi logic RAG
        result = answer_question(request.question, request.course_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))