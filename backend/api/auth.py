from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend.auth.users import get_user, verify_password
from backend.auth.security import create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginRequest):
    # 1. Tìm user (đã fix lookup lowercase)
    user = get_user(data.username)
    
    # 2. Kiểm tra user tồn tại
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Verify mật khẩu bằng passlib context
    is_valid = verify_password(data.password, user["password_hash"])
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 4. Tạo JWT Token nếu mọi thứ OK
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"]
    }