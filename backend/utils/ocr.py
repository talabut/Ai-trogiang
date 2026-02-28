# backend/utils/ocr.py

from typing import List, Dict
from paddleocr import PaddleOCR
import logging

logger = logging.getLogger(__name__)

_ocr = PaddleOCR(
    use_textline_orientation=True,
    lang="en"
)


def run_ocr(pdf_path: str) -> List[Dict]:
    """
    OCR scanned PDF → return page-level text blocks

    Output schema:
    [
        {
            "page_number": int,
            "text": str
        }
    ]
    """

    try:
        results = _ocr.ocr(pdf_path)
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

            # Expected structure:
            # line = [ [box], (text, confidence) ]
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
