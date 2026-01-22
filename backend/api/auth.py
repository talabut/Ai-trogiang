from fastapi import APIRouter
from pydantic import BaseModel

from backend.auth.users import authenticate
from backend.auth.security import create_access_token

router = APIRouter(prefix="/auth")


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(req: LoginRequest):
    user = authenticate(req.username, req.password)
    if not user:
        return {"error": "Invalid credentials"}

    token = create_access_token({
        "sub": user["username"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }
