# backend/rag/chunking.py

import re
from typing import List, Dict
import tiktoken

from backend.rag.canonicalize import get_canonical_hash

# ===============================
# CONFIG
# ===============================

TARGET_MIN = 400
TARGET_MAX = 600
OVERLAP = 100
MIN_CHUNK = 50

encoding = tiktoken.get_encoding("cl100k_base")


# ===============================
# TOKEN UTILS
# ===============================

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))


# ===============================
# STRUCTURE SPLIT
# ===============================

def split_by_structure(text: str) -> List[str]:
    text = text.replace("\r\n", "\n")

    heading_pattern = r"\n(?=[A-Z0-9][A-Z0-9\s\.]{3,}\n)"
    sections = re.split(heading_pattern, text)

    blocks = []
    for sec in sections:
        paragraphs = sec.split("\n\n")
        for p in paragraphs:
            p = p.strip()
            if p:
                blocks.append(p)

    return blocks


# ===============================
# MAIN CHUNKER
# ===============================

def chunk_single_text(text: str, page: int, source: str) -> List[Dict]:

    blocks = split_by_structure(text)

    chunks = []
    current_text = ""
    current_tokens = 0

    for block in blocks:
        block_tokens = count_tokens(block)

        # ---- FORCE SPLIT IF TOO LARGE ----
        if block_tokens > TARGET_MAX:
            tokens = encoding.encode(block)
            start = 0

            while start < len(tokens):
                end = min(start + TARGET_MAX, len(tokens))
                piece = encoding.decode(tokens[start:end])

                if count_tokens(piece) >= MIN_CHUNK:
                    chunk_data = {
                        "text": piece.strip(),
                        "page": page,
                        "source": source,
                        "token_count": count_tokens(piece),
                    }

                    chunk_data["chunk_id"] = get_canonical_hash(chunk_data)
                    chunks.append(chunk_data)

                start += TARGET_MAX - OVERLAP

            continue

        # ---- NORMAL ACCUMULATION ----
        if current_tokens + block_tokens <= TARGET_MAX:
            current_text += "\n\n" + block
            current_tokens += block_tokens
        else:
            if current_tokens >= MIN_CHUNK:
                chunk_data = {
                    "text": current_text.strip(),
                    "page": page,
                    "source": source,
                    "token_count": current_tokens,
                }

                chunk_data["chunk_id"] = get_canonical_hash(chunk_data)
                chunks.append(chunk_data)

            # overlap
            tokens = encoding.encode(current_text)
            overlap_tokens = tokens[-OVERLAP:] if len(tokens) > OVERLAP else tokens

            current_text = encoding.decode(overlap_tokens)
            current_tokens = count_tokens(current_text)

            current_text += "\n\n" + block
            current_tokens += block_tokens

    # ---- FINAL FLUSH ----
    if current_tokens >= MIN_CHUNK:
        chunk_data = {
            "text": current_text.strip(),
            "page": page,
            "source": source,
            "token_count": current_tokens,
        }

        chunk_data["chunk_id"] = get_canonical_hash(chunk_data)
        chunks.append(chunk_data)

    return chunks


# ===============================
# CANONICAL ENTRY POINT
# ===============================

def chunk_canonical_data(canonical_data: List[Dict]) -> List[Dict]:
    """
    Input:
    [
        {
            "page": int,
            "source": str,
            "lines": [str, str, ...]
        }
    ]

    Output:
    [
        {
            "text": str,
            "page": int,
            "source": str,
            "token_count": int,
            "chunk_id": str
        }
    ]
    """

    all_chunks = []

    for page_data in canonical_data:
        page = page_data.get("page", 1)
        source = page_data.get("source", "unknown")
        lines = page_data.get("lines", [])

        text = "\n\n".join(lines)

        page_chunks = chunk_single_text(
            text=text,
            page=page,
            source=source
        )

        all_chunks.extend(page_chunks)

    return all_chunks