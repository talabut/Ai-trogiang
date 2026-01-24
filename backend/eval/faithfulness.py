import re
from typing import Dict, Any, List


STOPWORDS = {
    "là", "và", "của", "trong", "cho", "với", "một", "các",
    "được", "khi", "này", "đó", "như", "để"
}


def normalize(text: str) -> List[str]:
    """
    Normalize text into keyword tokens
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9à-ỹ\s]", " ", text)
    tokens = text.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


def extract_claim_sentences(answer: str) -> List[str]:
    """
    Split answer into claim sentences (remove chunk tags)
    """
    clean = re.sub(r"\[CHUNK_\d+\]", "", answer)
    sentences = re.split(r"[.\n]", clean)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def check_faithfulness(
    answer: str,
    contexts: List[str],
    min_overlap_ratio: float = 0.3
) -> Dict[str, Any]:
    """
    Faithfulness check:
    - Each claim sentence must overlap sufficiently with context keywords
    """

    context_text = " ".join(contexts)
    context_tokens = set(normalize(context_text))

    claims = extract_claim_sentences(answer)

    if not claims:
        return {
            "faithful": False,
            "reason": "NO_CLAIM_SENTENCE",
            "details": "No valid claim sentence found in answer."
        }

    unfaithful_claims = []

    for claim in claims:
        claim_tokens = normalize(claim)

        if not claim_tokens:
            continue

        overlap = set(claim_tokens) & context_tokens
        overlap_ratio = len(overlap) / len(set(claim_tokens))

        if overlap_ratio < min_overlap_ratio:
            unfaithful_claims.append({
                "claim": claim,
                "overlap_ratio": round(overlap_ratio, 2)
            })

    if unfaithful_claims:
        return {
            "faithful": False,
            "reason": "LOW_CONTEXT_OVERLAP",
            "details": unfaithful_claims
        }

    return {
        "faithful": True,
        "reason": "OK",
        "details": "All claims sufficiently supported by context."
    }
