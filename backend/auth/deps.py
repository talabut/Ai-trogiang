from fastapi import Depends
from backend.auth.users import USERS_DB

# Mock user để các logic phía sau không bị crash
DEFAULT_USER = USERS_DB["teacher1"]

def get_current_user():
    """Bypass hoàn toàn - Luôn trả về user mặc định"""
    return DEFAULT_USER

def require_teacher(current_user=Depends(get_current_user)):
    """Bypass role check"""
    return current_user

def require_student(current_user=Depends(get_current_user)):
    """Bypass role check"""
    return current_user