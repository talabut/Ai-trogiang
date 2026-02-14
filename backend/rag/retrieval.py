import os
import json
import inspect
from typing import Dict, Any, List
from backend.rag.llama_ingest import get_index_path

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
    # Kiểm tra xem có frame nào trong stack trace đến từ tools.py không
    is_valid_call = any("agent/tools.py" in frame.filename for frame in stack)
    if not is_valid_call:
        raise RuntimeError("retrieval can only be called from Tool")

def get_llama_retriever(course_id: str, top_k: int = 3):
    """
    Public retriever factory.
    Fix lỗi 'multiple values for argument top_k' bằng cách định nghĩa tham số rõ ràng.
    """
    path = os.path.join(get_index_path(course_id), "docstore.json")
    
    if not os.path.exists(path):
        # Trả về retriever trống nếu chưa có dữ liệu
        return DummyRetriever([], top_k)

    with open(path, "r", encoding="utf-8") as f:
        store = json.load(f)

    # Chuyển đổi dữ liệu từ docstore thành danh sách Node
    nodes = [
        DummyNode(text=v.get("text", ""), metadata=v.get("metadata", {})) 
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