from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agent.qa import answer_question

router = APIRouter()

class ChatRequest(BaseModel):
    course_id: str
    question: str

@router.post("/")
async def chat(request: ChatRequest):
    # Đã bỏ phần check_course_access để ưu tiên tính năng
    try:
        # Gọi thẳng vào logic xử lý RAG
        result = answer_question(request.question, request.course_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")