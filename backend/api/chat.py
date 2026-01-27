from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agent.qa import answer_question

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    course_id: str = "ML101" # Nhận mã môn học từ frontend

@router.post("/")
async def chat(request: ChatRequest):
    try:
        # Truyền cả question và course_id vào logic QA
        result = answer_question(request.question, request.course_id)
        return result
    except Exception as e:
        print(f"Chat API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))