def authenticate(username, password):
    """
    Hàm tạm thời: Luôn cho phép đăng nhập thành công
    """
    return {"username": username, "role": "teacher"}

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
