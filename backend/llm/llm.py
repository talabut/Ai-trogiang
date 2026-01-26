import google.generativeai as genai

class GeminiLLM:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Lỗi gọi LLM: {str(e)}"

# Để dùng offline như cũ thì giữ nguyên class cũ của bạn
class OfflineLLM:
    def generate(self, prompt: str) -> str:
        return "Đây là câu trả lời mẫu từ hệ thống Offline. (Vui lòng cấu hình API Key để dùng thật)."

# Khởi tạo instance (Thay 'YOUR_KEY' nếu muốn dùng thật)
# llm_instance = GeminiLLM(api_key="YOUR_GEMINI_API_KEY")
llm_instance = OfflineLLM()

def get_llm():
    return llm_instance