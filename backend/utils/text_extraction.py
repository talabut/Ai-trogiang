import logging
import os
from pathlib import Path
from typing import List, Dict, Any

from pypdf import PdfReader
from pdf2image import convert_from_path
from docx import Document as DocxDocument

# Import module OCR đã có sẵn trong hệ thống
from backend.utils.ocr import ocr_image

# Cấu hình Logger
logger = logging.getLogger(__name__)

# Ngưỡng ký tự trung bình mỗi trang để quyết định dùng OCR
# Nếu pypdf lấy được ít hơn số này, coi là file scan
TEXT_DENSITY_THRESHOLD = 50 


def extract_text(file_path: str) -> List[Dict[str, Any]]:
    """
    Hàm entry point duy nhất để trích xuất văn bản.
    
    Args:
        file_path (str): Đường dẫn tới file cần xử lý.
        
    Returns:
        List[Dict]: Danh sách các trang văn bản với định dạng thống nhất:
        [
            {
                "page": int,      # Số trang (bắt đầu từ 1)
                "text": str,      # Nội dung văn bản thô
                "source": str     # Công cụ trích xuất ('pypdf', 'paddle_ocr', 'docx', 'text')
            },
            ...
        ]
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
    Xử lý PDF: Tự động phát hiện PDF văn bản hay PDF scan.
    """
    # 1. Thử trích xuất bằng pypdf (nhanh)
    extracted_pages = _extract_pdf_text_pypdf(file_path)

    # 2. Tính toán mật độ văn bản để phát hiện scan
    total_chars = sum(len(p["text"].strip()) for p in extracted_pages)
    num_pages = len(extracted_pages) if extracted_pages else 1
    avg_chars = total_chars / num_pages

    # 3. Nếu mật độ văn bản quá thấp, chuyển sang chế độ OCR
    if avg_chars < TEXT_DENSITY_THRESHOLD:
        logger.info(f"PDF density low ({avg_chars:.2f} chars/page). Switching to OCR mode.")
        return _extract_pdf_ocr(file_path)
    
    logger.info("PDF text extraction successful using pypdf.")
    return extracted_pages


def _extract_pdf_text_pypdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Trích xuất text từ PDF dạng text-based bằng pypdf.
    """
    results = []
    try:
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            results.append({
                "page": i + 1,
                "text": text,
                "source": "pypdf"
            })
    except Exception as e:
        logger.error(f"pypdf extraction failed: {e}")
        # Trả về list rỗng để logic chính quyết định fallback hoặc dừng
        return []
    
    return results


def _extract_pdf_ocr(file_path: str) -> List[Dict[str, Any]]:
    """
    Trích xuất text từ PDF dạng scan bằng cách chuyển sang ảnh và dùng PaddleOCR.
    """
    results = []
    try:
        # Chuyển PDF thành danh sách ảnh (PIL Images)
        # Lưu ý: poppler phải được cài đặt trong môi trường (docker/system)
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
        # Nếu lỗi convert ảnh hoặc OCR, trả về list rỗng hoặc lỗi cục bộ
        return []

    return results


def _process_docx(file_path: str) -> List[Dict[str, Any]]:
    """
    Xử lý file DOCX.
    DOCX không có khái niệm 'trang' cứng như PDF, ta gộp toàn bộ vào page 1 
    hoặc có thể tách theo section nếu cần thiết sau này.
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