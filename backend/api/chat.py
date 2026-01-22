from fastapi import APIRouter
from pydantic import BaseModel

from backend.agent.tutor_agent import get_tutor_agent

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/")
def chat(req: ChatRequest):
    try:
        chain, retriever = get_tutor_agent()
    except ValueError as e:
        return {
            "answer": str(e),
            "sources": [],
            "status": "NO_DOCUMENT"
        }

    # Retrieve docs for citation
    docs = retriever.get_relevant_documents(req.question)

    if not docs:
        return {
            "answer": "Không tìm thấy nội dung phù hợp trong tài liệu.",
            "sources": [],
            "status": "NO_MATCH"
        }

    answer = chain.invoke(req.question)

    sources = []
    seen = set()

    for doc in docs:
        src = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "N/A")

        key = f"{src}-{page}"
        if key not in seen:
            seen.add(key)
            sources.append({
                "file": src,
                "page": page
            })

    return {
        "answer": answer,
        "sources": sources,
        "status": "OK"
    }
