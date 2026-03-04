from typing import Optional

from pydantic import BaseModel


class QuizGenerateRequest(BaseModel):
    course_id: str
    num_questions: int = 5
    query: Optional[str] = None
    top_k: int = 30
