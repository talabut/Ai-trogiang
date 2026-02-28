from typing import List, Optional
from pydantic import BaseModel


class Evidence(BaseModel):
    text: str
    metadata: dict


class ChatRequest(BaseModel):
    question: str
    session_id: str
    course_id: str


class ChatResponse(BaseModel):
    answer: str
    evidence_count: int
    sources: List[str]
    ingest_status: str
    refusal: bool = False
    reason: Optional[str] = None
    tool_schema_version: str = "rag.v1"
