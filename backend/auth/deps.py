from fastapi import Header, HTTPException
from backend.auth.security import verify_token


def require_teacher(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)

    if not payload or payload.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Teacher only")

    return payload
