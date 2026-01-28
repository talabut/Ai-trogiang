import json
import re
from backend.llm.llm import llm_instance

def clean_json_response(raw_text: str) -> str:
    """
    Loại bỏ các ký tự Markdown thừa [cite: 65]
    """
    # Xử lý trường hợp LLM trả về ```json ... ``` hoặc văn bản bao quanh JSON
    json_match = re.search(r"(\{.*\}|\[.*\])", raw_text, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()
    return raw_text.strip()

def generate_lesson_plan(topic: str, context: str = ""):
    prompt = f"""
    Hãy đóng vai là một chuyên gia sư phạm.
    Chủ đề: {topic}
    Ngữ cảnh tài liệu: {context}
    
    Hãy tạo một giáo án chi tiết dưới định dạng JSON với các trường:
    - title, objectives, activities
    Chỉ trả về JSON. [cite: 66, 67, 68]
    """
    
    raw_response = llm_instance.invoke(prompt)
    cleaned_json = clean_json_response(raw_response)
    
    try:
        return json.loads(cleaned_json)
    except json.JSONDecodeError:
        # Fallback nếu JSON vẫn lỗi [cite: 69]
        return {
            "title": topic,
            "objectives": ["Không thể tạo mục tiêu tự động"],
            "activities": [],
            "error": "AI trả về định dạng không hợp lệ"
        }