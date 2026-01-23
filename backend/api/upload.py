from fastapi import APIRouter, UploadFile, Depends
import os
from backend.rag.ingest import ingest_document
from backend.auth.deps import get_current_user

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "data/raw_docs"

@router.post("/")
def upload(course_id: str, file: UploadFile, user=Depends(get_current_user)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    ingest_document(file_path, course_id)

    return {"status": "uploaded", "course_id": course_id}
