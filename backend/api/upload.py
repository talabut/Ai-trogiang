import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.rag.ingest import ingest_document

router = APIRouter()

UPLOAD_DIR = "data/raw_docs"

@router.post("/")
async def upload_document(course_id: str, file: UploadFile = File(...)):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    # FIX: Tạo tên file duy nhất tránh ghi đè [cite: 20]
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Ingest dữ liệu vào vector store theo course_id [cite: 24, 84]
        ingest_document(file_path, course_id)

        return {
            "message": f"Upload thành công file {file.filename}",
            "saved_as": unique_filename
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))