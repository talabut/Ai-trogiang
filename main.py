#D:\ai-tro-giang\main.py
import time
import logging
import traceback  # Thêm thư viện này để in lỗi chi tiết
import sys
import backend.infra.rag.llama_settings

# Cấu hình logging ép buộc in ra cả Console và File
logging.basicConfig(
    level=logging.DEBUG, # Chuyển sang DEBUG để xem chi tiết nhất
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout), # Ép in ra màn hình chính
        logging.FileHandler("debug_error.log", encoding="utf-8") # Ghi thêm vào file để chắc chắn không mất
    ]
)
logger = logging.getLogger("uvicorn") # Sử dụng logger của chính uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config.integrity_config import settings
from backend.api.dependencies import request_id_middleware
from backend.api import upload, chat
from backend.startup_validator import validate_startup
from backend.middleware.rate_limit import rate_limit

# Cấu hình logging để hiển thị lỗi đẹp hơn
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
def on_startup():
    validate_startup()

# --- MIDDLEWARE XỬ LÝ LỖI CHI TIẾT ---
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        # In toàn bộ lỗi ra Terminal để bạn debug
        logger.error("--- CÓ LỖI XẢY RA ---")
        traceback.print_exc() 
        
        # Trả về chi tiết lỗi cho Frontend (chỉ nên dùng khi đang code/dev)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc() # Dòng này giúp bạn biết lỗi ở file nào, dòng nào
            }
        )

app.middleware("http")(request_id_middleware)
app.middleware("http")(rate_limit)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Exception handler cho các lỗi xử lý chung
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": str(exc)
        }
    )

@app.get("/health")
def health():
    return {"status": "ok", "ts": time.time()}

app.include_router(upload.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")