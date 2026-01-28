from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from backend.auth.users import get_user, verify_password
from backend.auth.security import create_access_token
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Hỗ trợ cả OAuth2 Form (Swagger) và JSON (Frontend)
    """
    username, password = None, None
    
    # Kiểm tra xem là JSON hay Form
    content_type = request.headers.get("Content-Type", "")
    if "application/json" in content_type:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
    else:
        username = form_data.username
        password = form_data.password

    user = get_user(username)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user["role"]
    }