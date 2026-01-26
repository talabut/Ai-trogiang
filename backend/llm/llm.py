import os
try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class GeminiLLM:
    def __init__(self, api_key: str):
        self.client = None
        if HAS_GENAI and api_key:
            # Sử dụng thư viện google-genai mới nhất
            self.client = genai.Client(api_key=api_key)
            self.model_id = "gemini-1.5-flash"
        
    def generate(self, prompt: str) -> str:
        if not self.client:
            return "Hệ thống đang chạy Offline hoặc thiếu API Key. (Vui lòng cấu hình lại llm.py)"
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Lỗi Gemini API: {str(e)}"

# --- CẤU HÌNH ---
# 1. Nếu muốn dùng thật: Dán key vào đây
MY_API_KEY = "" 

# 2. Khởi tạo instance
if MY_API_KEY:
    llm_instance = GeminiLLM(api_key=MY_API_KEY)
else:
    # Nếu không có key, trả về class giả lập để không lỗi hệ thống
    class OfflineLLM:
        def generate(self, prompt: str):
            return "AI Trợ Giảng (Offline): Tài liệu đã được tìm thấy nhưng cần API Key để tóm tắt câu trả lời."
    llm_instance = OfflineLLM()

def get_llm():
    return llm_instance