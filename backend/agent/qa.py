from backend.rag.hybrid_retriever import hybrid_search
from backend.llm.llm import llm_instance

def answer_question(query: str, course_id: str):
    """
    Nhận câu hỏi, tìm kiếm tài liệu liên quan và trả lời.
    """
    # 1. Tìm kiếm ngữ cảnh từ nhiều nguồn (Hybrid)
    docs = hybrid_search(query, course_id)
    
    if not docs:
        return {
            "answer": "Xin lỗi, tôi không tìm thấy thông tin liên quan trong tài liệu của môn học này.",
            "sources": []
        }

    context = "\n\n".join([doc.page_content for doc in docs])
    
    # 2. Xây dựng Prompt chặt chẽ (Guardrails)
    prompt = f"""
    Bạn là một trợ lý giảng dạy thông minh. Hãy trả lời câu hỏi dựa TRỰC TIẾP vào ngữ cảnh dưới đây.
    Nếu ngữ cảnh không có thông tin, hãy nói rằng bạn không biết, đừng tự bịa ra câu trả lời.

    NGỮ CẢNH:
    {context}

    CÂU HỎI: {query}
    
    TRẢ LỜI:
    """

    # 3. Gọi LLM và xử lý kết quả
    response_text = llm_instance.invoke(prompt)
    
    # Lấy danh sách nguồn (metadata) để hiển thị cho người dùng
    sources = []
    for doc in docs:
        source_info = doc.metadata.get("source", "Tài liệu không tên")
        if source_info not in sources:
            sources.append(source_info)

    return {
        "answer": response_text.strip(),
        "sources": sources
    }