from fastapi import APIRouter, Depends
from backend.courses.service import create_course, list_courses_by_owner
from backend.auth.deps import get_current_user

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("/create")
def create(course_id: str, name: str, user=Depends(get_current_user)):
    return create_course(course_id, name, user["id"])

@router.get("/my")
def my_courses(user=Depends(get_current_user)):
    return list_courses_by_owner(user["id"])
