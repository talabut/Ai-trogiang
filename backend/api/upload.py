# backend/api/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.rag.ingest import ingest_document

router = APIRouter()

@router.post("/upload/")
def upload(file: UploadFile = File(...), course_id: str = "default"):
    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only .txt files are supported in MVP"
        )

    raw = file.file.read()

    try:
        content = raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File encoding must be UTF-8"
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Empty file"
        )

    texts = [content]
    metadatas = [{
        "course_id": course_id,
        "filename": file.filename
    }]

    return ingest_document(
        texts=texts,
        metadatas=metadatas
    )
