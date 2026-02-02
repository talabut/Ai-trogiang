import logging
from typing import List, Dict, Any
from backend.rag.retrieval import hybrid_search

logger = logging.getLogger("audit_trail")

SCHEMA_VERSION = "1.0"
# [III.8] Unified Threshold: Tool layer is the single source of truth
MIN_SCORE = 0.7 

REQUIRED_KEYS = {"text", "metadata", "score", "schema_version"}
FORBIDDEN_KEYS = {"answer"}
REQUIRED_METADATA_KEYS = {"doc_id", "page", "line_start", "line_end", "file_name"}

def _validate_evidence_item(item: Dict[str, Any]):
    """
    [III.9] Tool Interface Schema (Self-Assert)
    [III.7] Evidence-only Output (Tool-level)
    """
    keys = set(item.keys())
    
    # 1. Check for Forbidden Keys (Prevent Text Generation Leaks)
    if not keys.isdisjoint(FORBIDDEN_KEYS):
        raise ValueError(f"Tool Security Violation: Output contains forbidden keys: {keys & FORBIDDEN_KEYS}")

    # 2. Check for Required Keys
    if not REQUIRED_KEYS.issubset(keys):
        raise ValueError(f"Tool Schema Violation: Missing required keys: {REQUIRED_KEYS - keys}")

    # 3. Validate Metadata Structure
    metadata = item.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("Tool Schema Violation: metadata must be a dictionary")
    
    if not REQUIRED_METADATA_KEYS.issubset(metadata.keys()):
        raise ValueError(f"Tool Schema Violation: Metadata missing keys: {REQUIRED_METADATA_KEYS - metadata.keys()}")

    # 4. Validate Types (Basic)
    if not isinstance(item.get("text"), str) or not item["text"].strip():
        raise ValueError("Tool Data Violation: 'text' must be a non-empty string")
    
    if not isinstance(item.get("score"), (int, float)):
        raise ValueError("Tool Data Violation: 'score' must be a number")

def search_knowledge_base(query: str, course_id: str):
    # Get raw results from retrieval layer (which might use a lower internal threshold)
    results = hybrid_search(query, course_id)

    evidence = []

    for r in results:
        score = r.get("final_score", 0.0)
        
        # [III.8] Enforce strict threshold at Tool Layer
        if score < MIN_SCORE:
            continue

        item = {
            "text": r["text"],
            "metadata": {
                "doc_id": r["doc_id"],
                "page": r["page"],
                "line_start": r["line_start"],
                "line_end": r["line_end"],
                "file_name": r["file_name"],
            },
            "score": score,
            "schema_version": SCHEMA_VERSION
        }

        # [III.9] Validate immediately before returning
        _validate_evidence_item(item)
        
        evidence.append(item)

    return evidence