from fastapi import APIRouter, Depends, HTTPException
from backend.pedagogy.schemas import TaskRequest
from backend.pedagogy.generator import generate_task
from backend.auth.deps import get_current_user
from backend.auth.roles import UserRole

router = APIRouter(prefix="/pedagogy", tags=["Pedagogy"])

@router.post("/generate")
def generate(task: TaskRequest, user=Depends(get_current_user)):
    if user["role"] != UserRole.TEACHER:
        raise HTTPException(
            status_code=403,
            detail="Chỉ giảng viên mới được sử dụng chức năng này"
        )
    return generate_task(task)
