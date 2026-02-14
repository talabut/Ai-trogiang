from backend.utils.ocr import run_ocr


def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    PDF → OCR → TXT (BẮT BUỘC)
    """

    ocr_lines = run_ocr(pdf_path)

    normalized_lines = [
        line.strip()
        for line in ocr_lines
        if line and line.strip()
    ]

    return {
        "type": "TXT_CANONICAL",
        "lines": normalized_lines,
        "line_count": len(normalized_lines)
    }
