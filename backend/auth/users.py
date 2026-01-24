# backend/auth/users.py

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# Hash sẵn (tạo 1 lần rồi hardcode)
USERS_DB = {
    "teacher1": {
        "username": "teacher1",
        "password": "$2b$12$6b8KJ7u9yM3mY8qY1bQ3KOUxM8Y1zA0k9Ff5M9XqZxQxJw5s5Oe9a",  # 123456
        "role": "teacher"
    },
    "student1": {
        "username": "student1",
        "password": "$2b$12$6b8KJ7u9yM3mY8qY1bQ3KOUxM8Y1zA0k9Ff5M9XqZxQxJw5s5Oe9a",  # 123456
        "role": "student"
    }
}

def authenticate(username: str, password: str):
    user = USERS_DB.get(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user
