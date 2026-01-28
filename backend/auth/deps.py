from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.auth.security import verify_token
from backend.auth.roles import UserRole

# Sử dụng HTTPBearer để Swagger UI hiện nút "Authorize" (Green lock)
security = HTTPBearer()

def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    token = auth.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    role = payload.get("role")
    
    if not username or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token thiếu thông tin định danh"
        )
        
    return {
        "id": username,
        "role": role
    }

def require_teacher(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ giảng viên mới có quyền thực hiện hành động này"
        )
    return current_user