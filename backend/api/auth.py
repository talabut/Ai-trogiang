from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.auth.users import authenticate
from backend.auth.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    """
    Xác thực người dùng và cấp JWT Token thật
    """
    user = authenticate(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Tên đăng nhập hoặc mật khẩu không chính xác"
        )
    
    # Tạo JWT token chứa thông tin username và role
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"]
    }