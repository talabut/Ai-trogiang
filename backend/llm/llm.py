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
            return "AI đang Offline. Vui lòng kiểm tra API Key."
        try:
            # Lưu ý cú pháp model.generate_content của bản SDK mới
            response = self.client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Lỗi Gemini: {str(e)}"

class OfflineLLM:
    def invoke(self, prompt: str) -> str:
        return "AI (Offline): Tôi đã nhận được câu hỏi nhưng cần API Key để xử lý."

# --- CẤU HÌNH ---
MY_API_KEY = "" # Dán API Key vào đây

if MY_API_KEY:
    llm_instance = GeminiLLM(api_key=MY_API_KEY)
else:
    llm_instance = OfflineLLM()

def get_llm():
    return llm_instance