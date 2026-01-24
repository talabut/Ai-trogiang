def validate_groundedness(answer, sources):
    if not sources:
        raise ValueError(
            "Nội dung sinh ra không có căn cứ từ tài liệu."
        )
