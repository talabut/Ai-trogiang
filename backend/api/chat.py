from fastapi import APIRouter
from backend.agent.tutor_agent import get_tutor_agent
from backend.guardrails.citation import format_citations
from backend.guardrails.rate_limit import check_rate_limit
from backend.auth.deps import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

agent = get_tutor_agent()

@router.post("/")
def chat(query: str, user=Depends(get_current_user)):
    check_rate_limit(user["id"])
def chat(query: str):
    result = agent(query)

    return {
        "answer": result["result"],
        "citations": format_citations(result["source_documents"])
    }
