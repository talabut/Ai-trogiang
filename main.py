import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config.integrity_config import settings
from backend.api.dependencies import request_id_middleware
from backend.api import upload, chat
from backend.startup_validator import validate_startup
from backend.middleware.rate_limit import rate_limit
from backend.security.guard import enable_runtime_sandbox


logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
def on_startup():
    validate_startup()
    enable_runtime_sandbox() 

app.middleware("http")(request_id_middleware)
app.middleware("http")(rate_limit)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": "Internal server error"
        }
    )

@app.get("/health")
def health():
    return {"status": "ok", "ts": time.time()}

app.include_router(upload.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
