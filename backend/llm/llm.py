import os
try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class GeminiLLM:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key) if HAS_GENAI and api_key else None

    def invoke(self, prompt: str) -> str:
        if not self.client:
            return "Hệ thống đang chạy Offline. Vui lòng cấu hình API Key."
        try:
            # Cú pháp chuẩn của google-genai SDK 2026
            response = self.client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Lỗi Gemini API: {str(e)}"

class OfflineLLM:
    def invoke(self, prompt: str) -> str:
        return "AI (Chế độ Offline): Tôi đã nhận được câu hỏi nhưng cần API Key để xử lý thông tin."

# --- CẤU HÌNH API KEY ---
MY_API_KEY = "" # Dán Key của bạn vào đây

if MY_API_KEY:
    llm_instance = GeminiLLM(api_key=MY_API_KEY)
else:
    llm_instance = OfflineLLM()

def get_llm():
    return llm_instance