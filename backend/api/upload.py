#backend/api/upload.py
import os
import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.utils.text_extraction import extract_text_from_pdf
from backend.rag.canonicalize import canonicalize_document, FatalError
from backend.rag.chunking import chunk_canonical_data
from backend.rag.node_parser import parse_nodes
from backend.rag.llama_ingest import ingest_canonical_chunks
from backend.locks.ingest_lock import ingest_lock


router = APIRouter()


def get_raw_docs_path(course_id: str) -> str:
    return os.path.join("data", "raw_docs", course_id)


@router.post("/upload")
async def upload_file(
    course_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="ONLY_PDF_ALLOWED")

        with ingest_lock(course_id):

            # -------- SAVE RAW FILE --------
            raw_dir = get_raw_docs_path(course_id)
            os.makedirs(raw_dir, exist_ok=True)

            raw_file_path = os.path.join(raw_dir, file.filename)

            with open(raw_file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # -------- EXTRACT TEXT --------
            text = extract_text_from_pdf(raw_file_path)

            if not text or not text.strip():
                raise HTTPException(status_code=400, detail="EMPTY_EXTRACTED_TEXT")

            doc_id = str(uuid.uuid4())

            # 🔥 BẮT BUỘC CANONICAL PIPELINE
            try:
                canonical_data = canonicalize_document(
                    text=text,
                    source=file.filename
                )
            except FatalError as e:
                raise HTTPException(status_code=400, detail=str(e))

            # -------- CHUNK CANONICAL --------
            chunks = chunk_canonical_data(canonical_data)

            if not chunks:
                raise HTTPException(status_code=400, detail="NO_CHUNKS_CREATED")

            # -------- PARSE NODES --------
            nodes = parse_nodes(
                chunks=chunks,
                doc_id=doc_id,
                file_name=file.filename
            )

            if not nodes:
                raise HTTPException(status_code=400, detail="NO_VALID_NODES")

            # -------- INTERNAL INGEST --------
            result = ingest_canonical_chunks(
                chunks=nodes,
                course_id=course_id,
                filename=file.filename,
                doc_id=doc_id
            )

        return {
            "status": result.get("status"),
            "doc_id": doc_id,
            "new_chunks": result.get("new_chunks"),
            "total_pages": result.get("total_pages")
        }

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise