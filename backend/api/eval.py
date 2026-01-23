from fastapi import APIRouter, Depends
from backend.eval.runner import run_evaluation
from backend.auth.deps import get_current_user
from backend.auth.roles import UserRole

router = APIRouter(prefix="/eval", tags=["Evaluation"])


@router.post("/run")
def run_eval(user=Depends(get_current_user)):
    if user["role"] != UserRole.TEACHER:
        return {"error": "Chỉ giảng viên mới được chạy đánh giá"}
    return run_evaluation()
