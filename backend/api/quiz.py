from fastapi import APIRouter

from backend.quiz.schemas import QuizGenerateRequest
from backend.quiz.service import quiz_service

router = APIRouter()


@router.post("/quiz/generate")
def generate_quiz(req: QuizGenerateRequest):
    result = quiz_service.generate_quiz(
        course_id=req.course_id,
        num_questions=req.num_questions,
        query=req.query,
        top_k=req.top_k,
    )
    return result
