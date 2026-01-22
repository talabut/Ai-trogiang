def validate_groundedness(answer, sources):
    if not sources:
        raise ValueError("Không có tài liệu nguồn")
