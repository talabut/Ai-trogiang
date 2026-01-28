from passlib.context import CryptContext

# Khởi tạo context: passlib tự xử lý encoding và salt chuẩn cho bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So sánh mật khẩu plaintext và mật khẩu đã hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Tạo hash mới cho mật khẩu"""
    return pwd_context.hash(password)

# MẬT KHẨU TEST LÀ: 123456
# Hash này đã được tạo và kiểm tra bằng passlib
CLEAN_HASH = "$2b$12$R9h/lIPzMZ7E22NVjtORV.p6zif6oUaQW.mHnc6vSOfKy8nS.E8S."

USERS_DB = {
    "teacher1": {
        "username": "teacher1",
        "password_hash": CLEAN_HASH,
        "role": "teacher"
    },
    "student1": {
        "username": "student1",
        "password_hash": CLEAN_HASH,
        "role": "student"
    }
}

def get_user(username: str):
    return USERS_DB.get(username.lower())