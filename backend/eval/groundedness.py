import re
from typing import Dict, Any, List


CHUNK_PATTERN = re.compile(r"\[CHUNK_(\d+)\]")


def extract_chunk_ids(answer: str) -> List[int]:
    """
    Extract chunk indices from answer text.
    Example: [CHUNK_0], [CHUNK_2] → [0, 2]
    """
    return [int(x) for x in CHUNK_PATTERN.findall(answer)]


def check_groundedness(
    answer: str,
    sources: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Groundedness check:
    - Answer must contain chunk tags
    - Chunk tags must exist in retrieved sources
    """

    chunk_ids_in_answer = extract_chunk_ids(answer)

    if not chunk_ids_in_answer:
        return {
            "grounded": False,
            "reason": "NO_CHUNK_TAG",
            "details": "Answer does not contain any [CHUNK_x] tags."
        }

    valid_chunk_ids = {
        src.get("chunk_id") for src in sources
    }

    invalid_refs = [
        cid for cid in chunk_ids_in_answer
        if cid not in valid_chunk_ids
    ]

    if invalid_refs:
        return {
            "grounded": False,
            "reason": "INVALID_CHUNK_REFERENCE",
            "details": f"Referenced chunk(s) not in sources: {invalid_refs}"
        }

    return {
        "grounded": True,
        "reason": "OK",
        "details": f"All referenced chunks are valid: {chunk_ids_in_answer}"
    }
