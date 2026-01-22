from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_db = {
    "teacher1": {
        "username": "teacher1",
        "password": pwd_context.hash("123456"),
        "role": "teacher"
    },
    "student1": {
        "username": "student1",
        "password": pwd_context.hash("123456"),
        "role": "student"
    }
}


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def authenticate(username: str, password: str):
    user = users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user
