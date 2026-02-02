from fastapi import Request
from fastapi.responses import JSONResponse
import uuid

def success(data):
    return {
        "success": True,
        "data": data
    }

def error(code: str, message: str):
    return {
        "success": False,
        "error": code,
        "message": message
    }

async def request_id_middleware(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response
