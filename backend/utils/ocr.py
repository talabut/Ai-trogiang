# backend/utils/ocr.py
import logging
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image

logger = logging.getLogger(__name__)

# Khởi tạo OCR 1 lần (singleton)
_ocr = PaddleOCR(
    use_angle_cls=True,
    lang="vi",          # hoặc "en" nếu chỉ tiếng Anh
)

def ocr_image(image: Image.Image) -> str:
    """
    Nhận PIL Image -> trả về text thuần.
    Raise exception nếu OCR fail.
    """
    if image is None:
        raise ValueError("OCR_INPUT_IMAGE_NONE")

    try:
        img_array = np.array(image)
        result = _ocr.ocr(img_array, cls=True)

        if not result:
            return ""

        lines = []
        for block in result:
            for line in block:
                text = line[1][0]
                if text and text.strip():
                    lines.append(text.strip())

        return "\n".join(lines)

    except Exception as e:
        logger.exception("PADDLE_OCR_FAILED")
        raise RuntimeError(f"OCR_FAILED: {e}")
