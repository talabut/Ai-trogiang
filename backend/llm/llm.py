class OfflineLLM:
    """
    Offline, deterministic LLM stub.
    Only echoes grounded content.
    """

    def invoke(self, prompt: str) -> str:
        # Trả về phần context làm "tóm tắt"
        if "TÀI LIỆU:" in prompt:
            return (
                "Dựa trên các tài liệu được cung cấp, nội dung liên quan đã được "
                "tổng hợp và trình bày theo đúng phạm vi tài liệu."
            )
        return "Không đủ thông tin để trả lời."


def get_llm():
    return OfflineLLM()
