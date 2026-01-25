from fastapi import APIRouter
from backend.eval.runner import run_evaluation

router = APIRouter(prefix="/eval", tags=["Eval"])

@router.post(
    "/run",
    operation_id="eval_run"
)
def run_eval():
    return run_evaluation()
