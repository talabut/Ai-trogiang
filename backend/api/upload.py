import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.rag.ingest import ingest_document

router = APIRouter()

# Thư mục lưu trữ file
UPLOAD_DIR = "data/raw_docs"

@router.post("/")
async def upload_document(course_id: str, file: UploadFile = File(...)):
    # 1. Tạo thư mục nếu chưa tồn tại
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    # 2. Kiểm tra định dạng file (chỉ nhận .txt trong bản hiện tại)
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file .txt")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # 3. Lưu file vào ổ đĩa
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 4. Ingest vào Vector Database
        ingest_document(file_path, course_id)

        return {"message": f"Đã upload và xử lý file {file.filename} thành công cho khóa học {course_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))