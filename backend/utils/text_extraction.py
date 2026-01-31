import logging
import os
from pathlib import Path
from typing import List, Dict, Any

from pdf2image import convert_from_path
from docx import Document as DocxDocument

# Import module OCR đã có sẵn trong hệ thống
from backend.utils.ocr import ocr_image

# Cấu hình Logger
logger = logging.getLogger(__name__)

def extract_text(file_path: str) -> List[Dict[str, Any]]:
    """
    Hàm entry point duy nhất để trích xuất văn bản.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = Path(file_path).suffix.lower()

    try:
        if ext == ".pdf":
            return _process_pdf(file_path)
        elif ext == ".docx":
            return _process_docx(file_path)
        elif ext in [".txt", ".md"]:
            return _process_plain_text(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return []
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return []


def _process_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    FIX: Bắt buộc dùng OCR cho mọi file PDF (Force OCR).
    Bỏ qua pypdf và density check.
    """
    logger.info(f"Processing PDF with Force OCR: {file_path}")
    return _extract_pdf_ocr(file_path)


def _extract_pdf_ocr(file_path: str) -> List[Dict[str, Any]]:
    """
    Trích xuất text từ PDF bằng cách chuyển sang ảnh và dùng PaddleOCR.
    """
    results = []
    try:
        # Chuyển PDF thành danh sách ảnh (PIL Images)
        images = convert_from_path(file_path)
        
        for i, image in enumerate(images):
            # Gọi hàm ocr_image từ module ocr.py có sẵn
            text = ocr_image(image) or ""
            
            results.append({
                "page": i + 1,
                "text": text,
                "source": "paddle_ocr"
            })
            
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return []

    return results


def _process_docx(file_path: str) -> List[Dict[str, Any]]:
    """
    Xử lý file DOCX.
    """
    try:
        doc = DocxDocument(file_path)
        full_text = "\n".join([p.text for p in doc.paragraphs])
        return [{
            "page": 1,
            "text": full_text,
            "source": "docx"
        }]
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        return []


def _process_plain_text(file_path: str) -> List[Dict[str, Any]]:
    """
    Xử lý file TXT/MD.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return [{
            "page": 1,
            "text": content,
            "source": "text"
        }]
    except Exception as e:
        logger.error(f"Text file extraction failed: {e}")
        return []