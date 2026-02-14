import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse

LIMIT = 10
WINDOW = 60


def get_rate_store(request: Request):
    """
    Store rate-limit data on app.state
    => tránh leak giữa test cases
    """
    if not hasattr(request.app.state, "RATE"):
        request.app.state.RATE = defaultdict(list)
    return request.app.state.RATE


async def rate_limit(request: Request, call_next):
    ip = request.client.host
    now = time.time()

    RATE = get_rate_store(request)

    RATE[ip] = [t for t in RATE[ip] if now - t < WINDOW]

    if len(RATE[ip]) >= LIMIT:
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": "RATE_LIMITED",
                "message": "Too many requests"
            }
        )

    RATE[ip].append(now)
    return await call_next(request)
