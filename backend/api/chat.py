from fastapi import APIRouter
from pydantic import BaseModel

from backend.agent.tutor_agent import get_tutor_agent

router = APIRouter()
qa_chain = get_tutor_agent()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(req: ChatRequest):
    result = qa_chain(req.question)

    return {
        "answer": result["result"],
        "sources": [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in result["source_documents"]
        ]
    }
