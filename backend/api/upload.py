from fastapi import APIRouter, UploadFile, Depends
import os

from backend.utils.text_extraction import extract_text
from backend.rag.ingest import ingest_document
from backend.auth.deps import get_current_user

router = APIRouter(prefix="/upload", tags=["Upload"])
UPLOAD_DIR = "data/raw_docs"

@router.post(
    "/",
    operation_id="upload_document"
)
def upload(course_id: str, file: UploadFile, user=Depends(get_current_user)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    raw_text = extract_text(file_path)

    return ingest_document(
        raw_text=raw_text,
        source_file=file.filename
    )
