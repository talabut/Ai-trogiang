#D:\ai-tro-giang\backend\vectorstore\index_meta.py
import json
import os
import shutil
from datetime import datetime

from backend.rag.llama_ingest import (
    INDEX_VERSION,
    EMBEDDING_MODEL_TAG,
)

META_FILENAME = "index_meta.json"


def expected_meta(course_id: str):
    """
    🔥 Single Source of Truth cho metadata index.
    Phải đồng bộ với llama_ingest + retrieval layer.
    """
    return {
        "course_id": course_id,
        "index_version": INDEX_VERSION,
        "embedding_model_tag": EMBEDDING_MODEL_TAG,
        "timestamp": datetime.utcnow().isoformat()
    }


def write_meta(index_dir: str, course_id: str):
    os.makedirs(index_dir, exist_ok=True)

    meta_path = os.path.join(index_dir, META_FILENAME)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(
            expected_meta(course_id),
            f,
            indent=2,
            ensure_ascii=False,
            sort_keys=True
        )


def clear_index(index_dir: str):
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)


def assert_meta_compatible(index_dir: str, course_id: str = None):
    """
    🔥 Fail fast nếu metadata mismatch.
    """
    path = os.path.join(index_dir, META_FILENAME)

    # Nếu file meta không tồn tại
    if not os.path.exists(path):
        # Lúc startup, nếu thư mục trống thì không sao
        # Nhưng nếu có dữ liệu mà thiếu meta thì cảnh báo
        if os.listdir(index_dir):
            raise RuntimeError(f"INDEX_META_MISSING at {index_dir}")
        return

    # Nếu không truyền course_id (lúc startup), ta chỉ kiểm tra tính hợp lệ của file JSON
    # hoặc bỏ qua việc so sánh nội dung chi tiết.
    if course_id is None:
        return 

    with open(path, "r", encoding="utf-8") as f:
        stored = json.load(f)

    current = expected_meta(course_id)

    # So sánh (giữ nguyên logic của bạn)
    stored_compare = {k: v for k, v in stored.items() if k != "timestamp"}
    current_compare = {k: v for k, v in current.items() if k != "timestamp"}

    if stored_compare != current_compare:
        raise RuntimeError(f"INDEX_META_MISMATCH: Expected {current_compare}, got {stored_compare}")