from backend.rag.hybrid_retriever import hybrid_search
from backend.llm.llm import get_llm
from backend.agent.prompt import SYSTEM_PROMPT

def answer_question(question: str, course_id: str = "ML101"):
    # 1. Tìm tài liệu liên quan
    docs = hybrid_search(question, course_id)
    
    # 2. Tạo ngữ cảnh (Context)
    context = "\n".join([doc.page_content for doc in docs]) if docs else "Không tìm thấy tài liệu liên quan trong hệ thống."

    # 3. Tạo Prompt đầy đủ
    full_prompt = f"{SYSTEM_PROMPT}\n\nCONTEXT:\n{context}\n\nQUESTION:\n{question}"
    
    # 4. Gọi LLM xử lý
    llm = get_llm()
    response = llm.invoke(full_prompt)

    # 5. ĐẢM BẢO KẾT QUẢ LÀ STRING (Sửa lỗi này để chạy test)
    if isinstance(response, str):
        answer = response
    else:
        # Nếu là object từ Gemini SDK mới, lấy .text
        answer = getattr(response, 'text', str(response))

    return {
        "answer": answer,
        "sources": [{"content": d.page_content, "metadata": d.metadata} for d in docs]
    }