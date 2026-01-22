from backend.tools.search import search_docs

def generate_exam(topic: str):
    content = search_docs(topic)
    if not content:
        return "Không có tài liệu để tạo đề."

    return f"""
Tạo 5 câu hỏi từ nội dung sau:

{content[:1200]}

Yêu cầu:
- 3 câu lý thuyết
- 2 câu vận dụng
"""
