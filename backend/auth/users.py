# backend/auth/users.py

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def verify_password(plain: str, hashed: str) -> bool:
    if plain is None or hashed is None:
        return False

    # bcrypt giới hạn 72 bytes
    plain = plain.encode("utf-8")[:72].decode("utf-8", errors="ignore")

    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password)


# Hash sẵn (tạo 1 lần rồi hardcode)
USERS_DB = {
    "teacher1": {
        "username": "teacher1",
        "password": "$2b$12$mF8FEtZB5ia6zGDCaocUQO8sl1Ej1Rgkqg38fK800LB8LDfNJWObC",  # 123456
        "role": "teacher"
    },
    "student1": {
        "username": "student1",
        "password": "$2b$12$mF8FEtZB5ia6zGDCaocUQO8sl1Ej1Rgkqg38fK800LB8LDfNJWObC",  # 123456
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
