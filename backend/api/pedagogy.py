from fastapi import APIRouter

router = APIRouter(prefix="/pedagogy", tags=["Pedagogy"])

@router.post(
    "/generate",
    operation_id="pedagogy_generate"
)
def generate():
    return {"status": "ok"}
