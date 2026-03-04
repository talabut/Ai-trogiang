from fastapi import APIRouter

from backend.summarize.schemas import DocumentSummarizeRequest
from backend.summarize.service import summarize_service

router = APIRouter()


@router.post("/document/summarize")
def summarize_document(req: DocumentSummarizeRequest):
    result = summarize_service.summarize(
        course_id=req.course_id,
        summary_level=req.summary_level,
    )
    return result
