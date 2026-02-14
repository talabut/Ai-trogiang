from fastapi import APIRouter, UploadFile
from backend.utils.text_extraction import extract_text_from_pdf
from backend.rag.llama_ingest import ingest_txt_only

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile):
    if not file.filename.lower().endswith(".pdf"):
        raise RuntimeError("Only PDF allowed at upload layer")

    canonical_txt = extract_text_from_pdf(file.file)

    # ❌ KHÔNG ingest PDF
    # ✅ CHỈ ingest TXT canonical
    ingest_txt_only(canonical_txt)

    return {"status": "OK"}
