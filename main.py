# D:\ai-tro-giang\main.py
import logging
import sys
import time
import traceback

import backend.infra.rag.llama_settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import chat, document, quiz, upload
from backend.api.dependencies import request_id_middleware
from backend.config.integrity_config import settings
from backend.middleware.rate_limit import rate_limit
from backend.startup_validator import validate_startup

# Single logging config for development (DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("debug_error.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)


@app.on_event("startup")
def on_startup():
    validate_startup()


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        # Full traceback remains in server logs
        logger.exception("Unhandled application exception")

        debug_mode = bool(getattr(settings, "DEBUG", False))
        if debug_mode:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                },
            )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "INTERNAL_ERROR",
                "message": "Internal server error",
            },
        )


# Keep middleware order unchanged
app.middleware("http")(request_id_middleware)
app.middleware("http")(rate_limit)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def api_health():
    return {"status": "ok", "ts": time.time()}


app.include_router(upload.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(quiz.router, prefix="/api/v1")
app.include_router(document.router, prefix="/api/v1")
