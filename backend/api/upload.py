from fastapi import APIRouter, File, UploadFile, Query
import shutil
import os
from backend.rag.ingest import ingest_document

router = APIRouter()

UPLOAD_DIR = "backend/data/raw_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(
    file: UploadFile = File(...), 
    course_id: str = Query("ML101") # Fix: Thêm Query default để không bắt buộc
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Gọi hàm xử lý RAG
    ingest_document(file_path, course_id)
    
    return {
        "filename": file.filename, 
        "course_id": course_id, 
        "status": "ingested"
    }