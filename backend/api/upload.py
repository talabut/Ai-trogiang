from fastapi import APIRouter, File, UploadFile, Query
import shutil
import os
from pathlib import Path

from backend.utils.text_extraction import extract_text
from backend.rag.canonicalize import canonicalize_pages
# FIX: Import đúng tên hàm từ chunking.py
from backend.rag.chunking import chunk_canonical_data
from backend.rag.llama_ingest import ingest_canonical_chunks

router = APIRouter()

UPLOAD_DIR = "backend/data/raw_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    course_id: str = Query("ML101")
):
    # 1. Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Extract raw pages (Force OCR logic nằm trong utils)
    # EXPECT: List[Dict] [{page_num, text, ...}]
    raw_pages = extract_text(file_path)

    # 3. Canonicalize pages
    canonical_pages = canonicalize_pages(raw_pages)

    # 4. Chunking
    doc_id = Path(file.filename).stem
    # FIX: Truyền thêm doc_id vào hàm chunking
    chunks = chunk_canonical_data(canonical_pages, doc_id)

    # 5. Ingest into LlamaIndex
    ingest_canonical_chunks(
        chunks=chunks,
        course_id=course_id,
        file_name=file.filename,
        doc_id=doc_id
    )

    return {
        "filename": file.filename,
        "course_id": course_id,
        "doc_id": doc_id,
        "chunks": len(chunks),
        "status": "uploaded_and_ingested"
    }