# backend/rag/canonicalize.py

import hashlib
import json
import re
import unicodedata
from typing import Dict, List


class FatalError(Exception):
    pass


MIN_PARAGRAPH_LENGTH = 20  # tránh fragment 1–2 ký tự


def canonicalize_text(text: str) -> str:
    """
    Canonicalize extracted text into paragraph blocks.

    - Merge broken OCR lines into paragraphs
    - Remove tiny fragments
    - Normalize unicode
    - Collapse excessive whitespace
    """

    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)

    raw_blocks = text.split("\n\n")

    paragraphs = []

    for block in raw_blocks:
        block = block.strip()
        block = re.sub(r"\n", " ", block)
        block = " ".join(block.split())

        if len(block) < MIN_PARAGRAPH_LENGTH:
            continue

        paragraphs.append(block)

    return "\n\n".join(paragraphs)


def canonicalize_document(text: str, source: str) -> List[Dict]:
    """
    🔥 BẮT BUỘC: Convert raw extracted text → canonical format
    Output tương thích 100% với chunk_canonical_data()

    Return format:
    [
        {
            "page": int,
            "source": str,
            "lines": [str, str, ...]
        }
    ]
    """

    clean = canonicalize_text(text)

    if not clean:
        raise FatalError("CANONICAL_EMPTY_AFTER_CLEAN")

    paragraphs = clean.split("\n\n")

    return [
        {
            "page": 1,
            "source": source,
            "lines": paragraphs
        }
    ]


def get_canonical_hash(data: Dict) -> str:
    """
    Stable deterministic hash for chunk identity.
    Ensures identical content generates identical ID.
    """
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()