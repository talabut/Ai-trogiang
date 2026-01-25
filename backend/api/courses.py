from fastapi import APIRouter

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get(
    "/",
    operation_id="courses_list"
)
def list_courses():
    return []
