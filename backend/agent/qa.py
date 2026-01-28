from backend.rag.hybrid_retriever import hybrid_search
from backend.llm.llm import llm_instance
from backend.agent.prompt import SYSTEM_PROMPT

def answer_question(question: str, course_id: str) -> dict:
    # 1. Thực hiện tìm kiếm lai (Vector + BM25)
    context_docs = hybrid_search(query=question, course_id=course_id)

    if not context_docs:
        return {
            "answer": "Tôi không tìm thấy thông tin liên quan trong tài liệu của khóa học này.",
            "sources": []
        }

    # 2. Gom nhóm nội dung tìm được
    # Lấy top 3 đoạn văn bản có điểm số cao nhất để làm ngữ cảnh
    context_text = "\n---\n".join([doc["content"] for doc in context_docs[:3]])

    # 3. Tạo Prompt (Vẫn giữ cấu trúc để sau này dễ nâng cấp LLM thật)
    full_prompt = f"""{SYSTEM_PROMPT}

Ngữ cảnh tài liệu:
{context_text}

Câu hỏi người dùng: {question}
Trả lời:"""

    try:
        # Gọi Mock LLM xử lý local
        response = llm_instance.invoke(full_prompt)
    except Exception as e:
        response = f"Hệ thống đang bảo trì phần xử lý ngôn ngữ. Chi tiết: {str(e)}"

    return {
        "answer": response,
        "sources": context_docs
    }