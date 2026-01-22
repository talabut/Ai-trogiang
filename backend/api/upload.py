from fastapi import APIRouter, UploadFile, File
import shutil
import os

from backend.config import RAW_DOCS_PATH
from backend.rag.ingest import ingest_documents

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(RAW_DOCS_PATH, exist_ok=True)

    file_path = os.path.join(RAW_DOCS_PATH, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunks = ingest_documents()

    return {
        "message": "Upload & ingest thành công",
        "chunks_created": chunks
    }
