from typing import List, Optional

from pydantic import BaseModel


class Evidence(BaseModel):
    text: str
    metadata: dict


class RetrievalStats(BaseModel):
    nodes_found: int
    max_score: float


class ChatRequest(BaseModel):
    question: str
    session_id: str
    course_id: str


class ChatResponse(BaseModel):
    answer: Optional[str] = None
    evidence_count: int = 0
    sources: List[str] = []
    ingest_status: str = "READY"
    refusal: bool = False
    reason: Optional[str] = None
    message: Optional[str] = None
    retrieval_stats: Optional[RetrievalStats] = None
    tool_schema_version: str = "rag.v1"
