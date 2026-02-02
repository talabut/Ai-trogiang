from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config.integrity_config import settings
from backend.security.guard import safe_join
from backend.api.dependencies import success
from backend.locks.ingest_lock import acquire_ingest_lock, IngestLocked
import os

router = APIRouter()

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()

    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(413, "File too large")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Unsupported file type")

    path = safe_join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        f.write(content)

    return success({"filename": os.path.basename(path)})
async def upload_course(...):
    try:
        lock = acquire_ingest_lock(course_id)
    except IngestLocked:
        return {
            "success": False,
            "error": "INGEST_LOCKED",
            "message": "Ingest already in progress"
        }

    try:
        ingest_course_files(...)
        return {"success": True}
    finally:
        lock.release()