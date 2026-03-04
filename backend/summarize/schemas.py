from pydantic import BaseModel


class DocumentSummarizeRequest(BaseModel):
    course_id: str
    summary_level: str = "outline"
