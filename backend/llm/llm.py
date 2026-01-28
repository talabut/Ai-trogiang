import re

class LocalMockLLM:
    """
    Mock LLM Engine: Xử lý câu trả lời dựa trên Retrieval Context.
    Đảm bảo không phụ thuộc vào thư viện bên ngoài (g4f, openai, etc.)
    """
    def __init__(self, model_name: str = "offline-pedagogy-v1"):
        self.model_name = model_name

    def invoke(self, prompt: str) -> str:
        # 1. Trích xuất ngữ cảnh từ prompt (Dựa trên cấu trúc trong qa.py)
        # Tìm nội dung nằm giữa 'Ngữ cảnh tài liệu:' và 'Câu hỏi người dùng:'
        context_match = re.search(r"Ngữ cảnh tài liệu:(.*?)Câu hỏi người dùng:", prompt, re.DOTALL)
        
        if not context_match:
            return "Tôi không tìm thấy thông tin phù hợp trong tài liệu của khóa học này."

        context = context_match.group(1).strip()
        
        # 2. Logic Rule-based: Trả về đoạn văn bản phù hợp nhất từ context
        # Ở đây ta ưu tiên trả về toàn bộ ngữ cảnh đã được tìm thấy bởi RAG
        if len(context) > 5:
            return f"Dựa trên tài liệu khóa học, tôi xin giải đáp như sau:\n\n{context}"
        
        return "Tài liệu được cung cấp không đủ thông tin để trả lời câu hỏi này."

# Khởi tạo instance duy nhất cho toàn hệ thống
llm_instance = LocalMockLLM()

def get_llm():
    return llm_instance