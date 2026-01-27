import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from backend.rag.ingest import ingest_document
from backend.auth.deps import require_teacher

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("/{course_id}/upload")
def upload_document(
    course_id: str, 
    file: UploadFile = File(...), 
    user=Depends(require_teacher) # Chỉ Giáo viên mới được upload
):
    """
    Tải lên tài liệu và xử lý đưa vào Vector Store.
    Sửa lỗi: Tránh trùng tên file và kiểm tra thư mục tồn tại.
    """
    upload_dir = "data/raw_docs"
    
    # Đảm bảo thư mục lưu trữ tồn tại
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # FIX: Tạo tên file duy nhất bằng UUID để không bị ghi đè
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_location = os.path.join(upload_dir, unique_filename)

    try:
        # Lưu file vào ổ đĩa
        with open(file_location, "wb") as f:
            content = file.file.read()
            f.write(content)
        
        # Gọi module RAG để đánh index (Hàm ingest này đã được fix ở bước 1)
        ingest_document(file_location, course_id)
        
        return {
            "message": "Tải lên và xử lý tài liệu thành công",
            "original_name": file.filename,
            "saved_as": unique_filename
        }
    except Exception as e:
        # Xóa file nếu quá trình xử lý thất bại để tránh rác dữ liệu
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý file: {str(e)}")