from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/login",
    operation_id="auth_login"
)
def login(username: str, password: str):
    return {"status": "ok"}
