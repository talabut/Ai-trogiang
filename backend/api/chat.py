from fastapi import APIRouter, Depends
from backend.agent.tutor_agent import get_tutor_agent
from backend.auth.deps import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/")
def chat(course_id: str, query: str, user=Depends(get_current_user)):
    agent = get_tutor_agent(course_id)
    result = agent(query)

    return {
        "answer": result["result"],
        "sources": [
            d.metadata for d in result["source_documents"]
        ]
    }
