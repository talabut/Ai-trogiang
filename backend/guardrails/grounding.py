from typing import List

MIN_DOCS_REQUIRED = 1

def check_grounding(source_documents: List):
    if not source_documents or len(source_documents) < MIN_DOCS_REQUIRED:
        raise ValueError(
            "Không tìm thấy tài liệu liên quan. "
            "Hệ thống không thể trả lời để tránh sai lệch học thuật."
        )
