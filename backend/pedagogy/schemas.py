from pydantic import BaseModel
from typing import List, Optional

class TaskRequest(BaseModel):
    task_type: str   # lesson_plan | assignment | exam | rubric | quiz
    subject: str
    clo: Optional[List[str]] = None
    bloom_level: Optional[str] = None
    difficulty: Optional[str] = None
    num_items: Optional[int] = None
    duration_minutes: Optional[int] = None
