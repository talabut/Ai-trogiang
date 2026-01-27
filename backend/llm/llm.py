import os
import google.generativeai as genai
from typing import Optional

# Khuyến khích sử dụng biến môi trường để bảo mật
# Bạn có thể set bằng lệnh: export GEMINI_API_KEY="your_key"
API_KEY = os.getenv("GEMINI_API_KEY") or "YOUR_DEFAULT_API_KEY_IF_NEEDED"

class GeminiLLM:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        if not API_KEY or API_KEY == "YOUR_DEFAULT_API_KEY_IF_NEEDED":
            print("CẢNH BÁO: Chưa tìm thấy GEMINI_API_KEY. Hệ thống có thể không hoạt động.")
        
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel(model_name)

    def invoke(self, prompt: str) -> str:
        """
        Gửi prompt đến Gemini và trả về văn bản thuần túy.
        """
        try:
            response = self.model.generate_content(prompt)
            # Kiểm tra xem response có nội dung không trước khi truy cập .text
            if response and response.text:
                return response.text
            return ""
        except Exception as e:
            print(f"Lỗi khi gọi Gemini API: {e}")
            return f"Lỗi: Không thể kết nối với LLM. {str(e)}"

# Singleton instance để dùng chung trong toàn bộ app
llm_instance = GeminiLLM()