import logging
import numpy as np
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)

_ocr_engine = None

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        # lang='vi' hỗ trợ tiếng Việt, use_angle_cls để xoay ảnh nghiêng
        _ocr_engine = PaddleOCR(use_angle_cls=True, lang='vi', show_log=False)
    return _ocr_engine

def ocr_image(image_obj) -> str:
    """
    OCR ảnh PIL. Trả về text hoặc None nếu lỗi.
    """
    try:
        ocr = get_ocr_engine()
        # Chuyển PIL Image sang numpy array
        img_np = np.array(image_obj)
        result = ocr.ocr(img_np, cls=True)
        
        lines = []
        if result and result[0]:
            lines = [line[1][0] for line in result[0]]
        
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"❌ OCR Internal Error: {e}")
        return None