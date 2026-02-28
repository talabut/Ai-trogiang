import os
import json
import inspect
from typing import Dict, Any, List

from backend.rag.llama_ingest import (
    get_index_path,
    INDEX_VERSION,
    EMBEDDING_MODEL_TAG
)

# --- Dummy Classes để tương thích với cấu trúc Node của LlamaIndex ---

class DummyNode:
    def __init__(self, text: str, metadata: dict):
        self.text = text
        self.metadata = metadata

    def get_content(self):
        return self.text


class DummyRetriever:
    def __init__(self, nodes: List[DummyNode], top_k: int):
        self.nodes = nodes
        self.top_k = top_k

    def retrieve(self, query: str):
        # Trả về top_k kết quả đầu tiên (giả lập tìm kiếm)
        return self.nodes[:self.top_k]


# --- Core Functions ---

def _enforce_tool_only_call():
    """STRICT: Chỉ cho phép gọi từ agent/tools.py"""
    stack = inspect.stack()
    is_valid_call = any("agent/tools.py" in frame.filename for frame in stack)
    if not is_valid_call:
        raise RuntimeError("retrieval can only be called from Tool")


def _validate_index_meta(index_dir: str):
    """
    🔥 CRITICAL: Validate index_meta.json đồng bộ với ingest layer
    """
    meta_path = os.path.join(index_dir, "index_meta.json")

    if not os.path.exists(meta_path):
        raise RuntimeError("INDEX_META_MISSING")

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except Exception:
        raise RuntimeError("INDEX_META_CORRUPTED")

    if meta.get("index_version") != INDEX_VERSION:
        raise RuntimeError("INDEX_VERSION_MISMATCH")

    if meta.get("embedding_model_tag") != EMBEDDING_MODEL_TAG:
        raise RuntimeError("EMBEDDING_MODEL_MISMATCH")


def get_llama_retriever(course_id: str, top_k: int = 5):
    """
    Public retriever factory.
    Đồng bộ persist path với ingest layer.
    """

    index_dir = get_index_path(course_id)
    store_path = os.path.join(index_dir, "docstore.json")

    if not os.path.exists(index_dir):
        raise RuntimeError("INDEX_DIR_NOT_FOUND")

    # 🔥 Validate meta trước khi load docstore
    _validate_index_meta(index_dir)

    if not os.path.exists(store_path):
        return DummyRetriever([], top_k)

    with open(store_path, "r", encoding="utf-8") as f:
        store = json.load(f)

    nodes = [
        DummyNode(
            text=v.get("text", ""),
            metadata=v.get("metadata", {})
        )
        for v in store.values()
    ]

    return DummyRetriever(nodes, top_k)


def retrieve_knowledge(query: str, course_id: str, top_k: int = 3):
    """
    Hàm thực hiện retrieval chính thống.
    """
    _enforce_tool_only_call()

    retriever = get_llama_retriever(course_id=course_id, top_k=top_k)
    nodes = retriever.retrieve(query)

    evidences = []
    sources = set()

    for node in nodes:
        evidences.append({
            "text": node.text,
            "metadata": node.metadata
        })
        if "file_name" in node.metadata:
            sources.add(node.metadata["file_name"])

    return {
        "answer": evidences[0]["text"] if evidences else "",
        "evidences": evidences,
        "sources": list(sources),
    }


def simple_search(query: str, nodes: list, top_k: int = 3):
    query = query.lower()
    scored = []

    for node in nodes:
        text = node["text"].lower()
        score = text.count(query)

        if score > 0:
            scored.append((score, node))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [n for _, n in scored[:top_k]]