from fastapi import APIRouter
from pydantic import BaseModel

from backend.tools.exam import generate_exam

router = APIRouter()

class ExamRequest(BaseModel):
    topic: str

@router.post("/")
def create_exam(req: ExamRequest):
    return {
        "exam": generate_exam(req.topic)
    }
