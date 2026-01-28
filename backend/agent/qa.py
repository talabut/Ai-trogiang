from backend.rag.hybrid_retriever import hybrid_search
from backend.llm.llm import llm_instance
from backend.agent.prompt import SYSTEM_PROMPT

def answer_question(question: str, course_id: str = "default_course") -> dict:
    """
    Logic trả lời câu hỏi RAG.
    FIX: Thêm default course_id và handle out-of-scope.
    """
    # 1. Tìm kiếm context
    context_docs = hybrid_search(query=question, course_id=course_id)

    # 2. Guardrail: Nếu không tìm thấy tài liệu (test_out_of_scope_question)
    if not context_docs:
        return {
            "answer": "Tôi không tìm thấy thông tin liên quan trong tài liệu hoặc câu hỏi nằm ngoài phạm vi hỗ trợ.",
            "sources": []
        }

    # 3. Chuẩn bị Prompt
    context_text = "\n---\n".join([doc["content"] for doc in context_docs[:3]])
    full_prompt = f"{SYSTEM_PROMPT}\n\nNgữ cảnh:\n{context_text}\n\nCâu hỏi: {question}\nTrả lời:"

    try:
        response = llm_instance.invoke(full_prompt)
        return {
            "answer": response,
            "sources": context_docs
        }
    except Exception as e:
        return {
            "answer": f"Đã xảy ra lỗi khi xử lý: {str(e)}",
            "sources": []
        }