import json
import re
from backend.llm.llm import llm_instance

def clean_json_response(raw_text: str) -> str:
    """
    Loại bỏ các ký tự Markdown thừa như ```json ... ``` 
    mà LLM thường trả về để tránh lỗi json.loads.
    """
    # Tìm nội dung nằm giữa cặp dấu ```json và ``` hoặc ```
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
    if json_match:
        return json_match.group(1).strip()
    return raw_text.strip()

def generate_lesson_plan(topic: str, context: str = ""):
    """
    Tạo giáo án từ AI dựa trên chủ đề và ngữ cảnh tài liệu.
    """
    prompt = f"""
    Hãy đóng vai là một chuyên gia sư phạm. Dựa trên thông tin sau:
    Chủ đề: {topic}
    Ngữ cảnh tài liệu: {context}
    
    Hãy tạo một giáo án chi tiết dưới định dạng JSON với các trường:
    - title: Tiêu đề
    - objectives: Danh sách mục tiêu
    - activities: Danh sách các hoạt động (mỗi hoạt động gồm name và duration)
    
    Chỉ trả về JSON, không giải thích gì thêm.
    """
    
    raw_response = llm_instance.invoke(prompt)
    
    # Sửa lỗi: Làm sạch chuỗi trước khi parse JSON
    cleaned_json = clean_json_response(raw_response)
    
    try:
        plan = json.loads(cleaned_json)
        return plan
    except json.JSONDecodeError as e:
        print(f"Lỗi parse JSON: {e}. Raw: {raw_response}")
        return {
            "error": "Không thể giải mã kết quả từ AI",
            "raw": raw_response
        }

def generate_quiz(context: str, num_questions: int = 5):
    """
    Tạo câu hỏi trắc nghiệm từ ngữ cảnh.
    """
    prompt = f"""
    Dựa trên nội dung sau: {context}
    Tạo {num_questions} câu hỏi trắc nghiệm JSON định dạng:
    [
      {{"question": "...", "options": ["A", "B", "C", "D"], "answer": "..."}}
    ]
    """
    
    raw_response = llm_instance.invoke(prompt)
    cleaned_json = clean_json_response(raw_response)
    
    try:
        return json.loads(cleaned_json)
    except json.JSONDecodeError:
        return []