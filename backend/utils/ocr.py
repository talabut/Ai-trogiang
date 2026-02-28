# backend/utils/ocr.py

from typing import List, Dict
from paddleocr import PaddleOCR
import logging
from threading import Lock

logger = logging.getLogger(__name__)

_ocr_instance = None
_ocr_lock = Lock()


def get_ocr() -> PaddleOCR:
    """
    Lazy singleton initializer for PaddleOCR.
    Only loads model when first used.
    Thread-safe.
    """
    global _ocr_instance

    if _ocr_instance is None:
        with _ocr_lock:
            if _ocr_instance is None:
                logger.info("[OCR INIT] Loading PaddleOCR model...")
                _ocr_instance = PaddleOCR(
                    use_textline_orientation=True,
                    lang="en"
                )
                logger.info("[OCR INIT DONE]")

    return _ocr_instance


def run_ocr(pdf_path: str) -> List[Dict]:
    """
    OCR scanned PDF → return page-level text blocks
    """

    try:
        ocr = get_ocr()
        results = ocr.ocr(pdf_path)
    except Exception as e:
        logger.error(f"[OCR ERROR] {pdf_path}: {e}")
        return []

    if not results or not isinstance(results, list):
        return []

    pages_output = []

    for page_idx, page in enumerate(results):

        if not page or not isinstance(page, list):
            continue

        page_lines = []

        for line in page:

            if (
                not line
                or not isinstance(line, list)
                or len(line) < 2
                or not isinstance(line[1], (list, tuple))
                or len(line[1]) < 1
            ):
                continue

            text = line[1][0]

            if not isinstance(text, str):
                continue

            text = text.strip()
            if not text:
                continue

            page_lines.append(text)

        if page_lines:
            page_text = "\n".join(page_lines)

            pages_output.append({
                "page_number": page_idx + 1,
                "text": page_text
            })

    logger.info(
        f"[OCR DONE] File: {pdf_path} | Pages: {len(pages_output)}"
    )

    return pages_output