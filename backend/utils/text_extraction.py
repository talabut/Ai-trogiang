# backend/utils/text_extraction.py

import re
import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from backend.utils.ocr import run_ocr

logger = logging.getLogger(__name__)


# =========================
# TEXT NORMALIZATION
# =========================

def normalize_text(text: str) -> str:
    """
    Clean text before chunking:
    - Ensure UTF-8
    - Remove control characters
    - Merge hyphen line breaks
    - Collapse multiple newlines
    - Collapse multiple spaces
    """

    if not text:
        return ""

    # Ensure UTF-8
    text = text.encode("utf-8", errors="ignore").decode("utf-8")

    # Remove control characters (except newline)
    text = "".join(
    	ch for ch in text
   	 if ch.isprintable() or ch == "\n"
   )

    # Merge hyphen line break: exam-\nple → example
    text = re.sub(r"-\n(\w)", r"\1", text)

    # Replace single newline inside paragraph with space
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # Collapse multiple newlines
    text = re.sub(r"\n{2,}", "\n\n", text)

    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


# =========================
# MAIN EXTRACTION
# =========================

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF.
    Strategy:
    1. Try direct PDF text extraction
    2. If empty → fallback OCR
    3. Normalize clean text
    4. Return single cleaned string
    """

    pdf_path = str(Path(pdf_path))

    raw_text: Optional[str] = ""

    # -------------------------
    # 1️⃣ Try PDF text extraction
    # -------------------------
    try:
        doc = fitz.open(pdf_path)
        pages = []

        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                pages.append(page_text)

        raw_text = "\n".join(pages)
        doc.close()

    except Exception as e:
        logger.error(f"[PDF TEXT ERROR] {pdf_path}: {e}")

    # -------------------------
    # 2️⃣ Fallback OCR if empty
    # -------------------------
    if not raw_text or len(raw_text.strip()) < 50:
        logger.info(f"[OCR FALLBACK] Running OCR for {pdf_path}")

        ocr_lines = run_ocr(pdf_path)

        if not ocr_lines:
            logger.warning(f"[OCR FAILED] {pdf_path}")
            return ""

        raw_text = "\n".join(
            line["text"].strip()
            for line in ocr_lines
            if line.get("text")
        )

    # -------------------------
    # 3️⃣ Normalize
    # -------------------------
    cleaned_text = normalize_text(raw_text)

    # -------------------------
    # 4️⃣ Log ingestion metrics
    # -------------------------
    logger.info(
        f"[INGESTION] File: {pdf_path} | "
        f"Raw chars: {len(raw_text)} | "
        f"Clean chars: {len(cleaned_text)}"
    )

    return cleaned_text
