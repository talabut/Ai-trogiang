import os
import json
import hashlib
from typing import List, Dict, Any
from backend.rag.canonicalize import canonicalize_text

INDEX_VERSION = "v1.0"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def get_index_path(course_id: str) -> str:
    """Trả về đường dẫn lưu trữ index dựa trên course_id."""
    return os.path.join("backend", "data", course_id)

def ingest_canonical_chunks(
    chunks: List[Dict[str, Any]], 
    course_id: str, 
    filename: str, 
    doc_id: str
):
    """
    Xử lý Ingest với các tính năng:
    - Signature: Ghi nhận version và model embedding.
    - Dedup chunk: Sử dụng SHA256 hash của text để tránh lưu trùng.
    - Metadata: Lưu trữ đầy đủ vị trí (page, line) và nguồn gốc.
    """
    path = get_index_path(course_id)
    os.makedirs(path, exist_ok=True)

    store_path = os.path.join(path, "docstore.json")
    vector_path = os.path.join(path, "default__vector_store.json")

    # Load dữ liệu hiện có để kiểm tra trùng lặp
    existing = {}
    if os.path.exists(store_path):
        try:
            with open(store_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = {}

    for c in chunks:
        # 1. Chuẩn hóa text trước khi hash để đảm bảo dedup chính xác
        clean_text = canonicalize_text(c["text"])
        
        # 2. Tạo Signature (UID) cho chunk dựa trên nội dung
        uid = hashlib.sha256(clean_text.encode()).hexdigest()
        
        # 3. Dedup: Nếu đã tồn tại chunk này thì bỏ qua
        if uid in existing:
            continue

        # 4. Metadata đầy đủ
        existing[uid] = {
            "text": clean_text,
            "metadata": {
                "doc_id": doc_id,
                "file_name": filename,
                "page": c.get("page", 0),
                "line_start": c.get("line_start", 0),
                "line_end": c.get("line_end", 0),
                "index_version": INDEX_VERSION,
                "embedding_model": EMBEDDING_MODEL,
            }
        }

    # Lưu lại docstore đã cập nhật
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    # Khởi tạo vector store trống nếu chưa có để tránh lỗi load
    if not os.path.exists(vector_path):
        with open(vector_path, "w") as f:
            json.dump({}, f)

def ingest_txt_only(text: str, course_id: str, filename: str, doc_id: str):
    """Hàm wrapper cho các request chỉ có text thô."""
    # Giả lập 1 chunk duy nhất cho file txt đơn giản
    chunks = [{
        "text": text,
        "page": 1,
        "line_start": 1,
        "line_end": len(text.splitlines())
    }]
    return ingest_canonical_chunks(chunks, course_id, filename, doc_id)