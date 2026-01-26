from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agent.qa import answer_question

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    course_id: str = "ML101" # Thêm dòng này để khớp với hàm answer_question

@router.post("/")
async def chat(request: ChatRequest):
    try:
        # Bây giờ bạn đã có thể truyền request.course_id vào đây
        result = answer_question(request.question, request.course_id)
        return result
    except Exception as e:
        print(f"Lỗi tại Chat API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))