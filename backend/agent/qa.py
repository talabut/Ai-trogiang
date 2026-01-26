from backend.rag.hybrid_retriever import hybrid_search
from backend.llm.llm import get_llm
from backend.agent.prompt import SYSTEM_PROMPT

def answer_question(question: str, course_id: str = "ML101"):
    # 1. Tìm tài liệu
    docs = hybrid_search(question, course_id)
    context = "\n".join([doc.page_content for doc in docs]) if docs else "Không tìm thấy tài liệu liên quan."

    # 2. Tạo Prompt
    full_prompt = f"{SYSTEM_PROMPT}\n\nCONTEXT:\n{context}\n\nQUESTION:\n{question}"
    
    # 3. Gọi LLM
    llm = get_llm()
    response = llm.invoke(full_prompt)

    # 4. Kiểm tra nếu response là object (Gemini SDK mới) thì lấy text
    answer = response if isinstance(response, str) else getattr(response, 'text', str(response))

    return {
        "answer": answer,
        "sources": [{"content": d.page_content, "metadata": d.metadata} for d in docs]
    }