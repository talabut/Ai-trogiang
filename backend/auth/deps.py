from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.auth.security import verify_token
from backend.auth.roles import UserRole

security = HTTPBearer()

def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    Middleware xác thực: Giải mã Token để lấy thông tin người dùng.
    Sửa lỗi: Thay thế dữ liệu mock bằng việc verify Token thật từ header.
    """
    payload = verify_token(auth.credentials)
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
    """
    Helper để bắt buộc quyền Giáo viên cho các API nhạy cảm (như upload)
    """
    if current_user["role"] != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện hành động này"
        )
    return current_user