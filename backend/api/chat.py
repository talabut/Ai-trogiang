from fastapi import APIRouter, Body
from backend.api.schemas import APIResponse
from backend.services.agent import AgentService

router = APIRouter()
agent = AgentService()

@router.post("/chat/query", response_model=APIResponse)
async def chat_query(question: str = Body(..., embed=True)):
    q = question.strip()
    if not q:
        return APIResponse(success=False, error="EMPTY_INPUT", message="Empty input")
    if len(q) > 2000:
        return APIResponse(success=False, error="INPUT_TOO_LONG", message="Too long")
    answer = await agent.ask(q, session_id="default")
    return APIResponse(success=True, data={"answer": answer})
