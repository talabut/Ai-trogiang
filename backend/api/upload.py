import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.rag.ingest import ingest_document

router = APIRouter()

UPLOAD_DIR = "data/raw_docs"

@router.post("/")
async def upload_document(course_id: str, file: UploadFile = File(...)):
    # Tạo thư mục nếu chưa có
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Ghi file vào ổ đĩa
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Ingest dữ liệu (chuyển văn bản thành vector)
        ingest_document(file_path, course_id)

        return {"message": f"Upload thành công file {file.filename}"}
    except Exception as e:
        # Trả về lỗi chi tiết để debug
        raise HTTPException(status_code=500, detail=str(e))