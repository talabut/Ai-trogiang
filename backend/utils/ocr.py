# FILE: backend/utils/ocr.py
from paddleocr import PaddleOCR

_ocr = PaddleOCR(
    use_textline_orientation=True,
    lang="en"
)

def run_ocr(image_path: str):
    """
    Mandatory OCR for scanned PDFs.
    Output schema:
    {
      text: str,
      page: int,
      line_start: int,
      line_end: int
    }
    """
    results = _ocr.ocr(image_path, cls=True)

    output = []
    line_counter = 0

    for page_idx, page in enumerate(results):
        for line in page:
            text = line[1][0]
            if not text.strip():
                continue

            output.append({
                "text": text,
                "page": page_idx + 1,
                "line_start": line_counter,
                "line_end": line_counter,
            })
            line_counter += 1

    return output
