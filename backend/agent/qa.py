from backend.rag.hybrid_retriever import hybrid_search
from backend.llm.llm import llm_instance
from backend.agent.prompt import SYSTEM_PROMPT


def answer_question(question: str, course_id: str) -> dict:
    context_docs = hybrid_search(query=question, course_id=course_id)

    if not context_docs:
        return {
            "answer": "Tôi không tìm thấy thông tin liên quan trong tài liệu của khóa học này.",
            "sources": []
        }

    context_text = "\n---\n".join([doc["content"] for doc in context_docs])

    full_prompt = f"""{SYSTEM_PROMPT}

Ngữ cảnh tài liệu:
{context_text}

Câu hỏi người dùng: {question}
Trả lời:"""

    try:
        response = llm_instance.invoke(full_prompt)
    except Exception as e:
        response = f"Lỗi khi kết nối với AI: {str(e)}"

    return {
        "answer": response,
        "sources": context_docs
    }
