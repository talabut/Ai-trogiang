from fastapi import APIRouter, UploadFile, File, Depends

router = APIRouter()

# ĐÃ VÔ HIỆU HÓA ĐỂ DÙNG CHUNG /upload/ CHO MVP
# @router.post("/{course_id}/upload")
# async def upload_to_course(course_id: str, file: UploadFile = File(...)):
#     return {"message": "Deprecated. Use /upload/ instead"}