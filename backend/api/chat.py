from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from backend.agent.tutor_agent import get_tutor_agent
from backend.auth.security import verify_token

router = APIRouter()
qa_chain = get_tutor_agent()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(req: ChatRequest, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

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
