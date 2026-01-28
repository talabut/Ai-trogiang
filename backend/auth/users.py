from passlib.context import CryptContext

# Khởi tạo context để hash và verify mật khẩu
# Dùng schem bcrypt để đảm bảo an toàn
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Sử dụng passlib để verify. 
    Nó tự động xử lý encoding và salt nội bộ.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

# MẬT KHẨU TEST: 123456
# Đây là hash chuẩn được tạo từ passlib.hash("123456")
VALID_HASH = "$2b$12$R9h/lIPzMZ7E22NVjtORV.p6zif6oUaQW.mHnc6vSOfKy8nS.E8S."

USERS_DB = {
    "teacher1": {
        "username": "teacher1",
        "password_hash": VALID_HASH,
        "role": "teacher",
        "full_name": "Giảng viên A"
    },
    "student1": {
        "username": "student1",
        "password_hash": VALID_HASH,
        "role": "student",
        "full_name": "Sinh viên B"
    }
}

def get_user(username: str):
    # Dùng lowercase để tránh lỗi do nhập liệu
    return USERS_DB.get(username.lower())