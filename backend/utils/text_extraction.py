import logging
import os
from pathlib import Path
from typing import List, Dict, Any
from pdf2image import convert_from_path
from docx import Document as DocxDocument
from backend.utils.ocr import ocr_image

logger = logging.getLogger(__name__)

# --- CONFIG ---
MIN_TOTAL_CHARS = 10  # Dưới 10 ký tự coi như file rác/rỗng

def extract_text(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = Path(file_path).suffix.lower()
    raw_pages = []

    try:
        if ext == ".pdf":
            raw_pages = _process_pdf(file_path)
        elif ext == ".docx":
            raw_pages = _process_docx(file_path)
        elif ext in [".txt", ".md"]:
            raw_pages = _process_plain_text(file_path)
        else:
            raise ValueError(f"UNSUPPORTED_FILE_TYPE: {ext}")
    except Exception as e:
        logger.error(f"EXTRACTION_CRASH: {file_path} | {str(e)}")
        raise e  # Re-raise để background task bắt được

    # --- INTEGRITY CHECK ---
    total_chars = sum(len(p.get("text", "").strip()) for p in raw_pages)
    if total_chars < MIN_TOTAL_CHARS:
        error_msg = f"DOCUMENT_EMPTY_OR_NOISE: {file_path} (chars={total_chars})"
        logger.error(error_msg)
        raise ValueError(error_msg)

    return raw_pages

def _process_pdf(file_path: str) -> List[Dict[str, Any]]:
    # Force OCR strict mode
    logger.info(f"Processing PDF strict OCR: {file_path}")
    return _extract_pdf_ocr(file_path)

def _extract_pdf_ocr(file_path: str) -> List[Dict[str, Any]]:
    results = []
    try:
        images = convert_from_path(file_path)
        if not images:
             raise ValueError("PDF_HAS_NO_PAGES")

        for i, image in enumerate(images):
            text = ocr_image(image) or ""
            # Chỉ append nếu có text thực sự để tiết kiệm RAM xử lý sau này
            if text.strip():
                results.append({
                    "page": i + 1,
                    "text": text,
                    "source": "paddle_ocr"
                })
    except Exception as e:
        raise RuntimeError(f"OCR_ENGINE_FAILURE: {str(e)}")
    
    return results

def _process_docx(file_path: str) -> List[Dict[str, Any]]:
    doc = DocxDocument(file_path)
    full_text = "\n".join([p.text for p in doc.paragraphs])
    return [{"page": 1, "text": full_text, "source": "docx"}]

def _process_plain_text(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    return [{"page": 1, "text": content, "source": "text"}]