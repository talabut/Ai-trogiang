import bcrypt

def hash_password(password: str) -> str:
    # FIX: Encode chuỗi sang utf-8 TRƯỚC khi băm và không cắt thủ công 72 ký tự
    # Bcrypt tự xử lý giới hạn này trên byte stream một cách an toàn
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False