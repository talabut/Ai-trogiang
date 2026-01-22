import shutil
from fastapi import APIRouter, UploadFile, Depends

from backend.auth.deps import require_teacher
from backend.rag.ingest import ingest

UPLOAD_DIR = "data/raw_docs"

router = APIRouter(prefix="/upload")


@router.post("/")
def upload_file(
    file: UploadFile,
    user=Depends(require_teacher)
):
    path = f"{UPLOAD_DIR}/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingest()

    return {
        "status": "uploaded & ingested",
        "filename": file.filename
    }
