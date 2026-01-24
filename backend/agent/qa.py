# backend/agent/qa.py

from typing import List
from langchain.schema import Document
from backend.vectorstore.faiss_store import get_faiss_store
from backend.llm.llm import get_llm

# =====================
# CONFIG
# =====================
SIMILARITY_THRESHOLD = 0.4
TOP_K = 5


def retrieve_context(question: str) -> List[Document]:
    """
    Retrieve documents with similarity score filtering
    """

    vectorstore = get_faiss_store()

    results = vectorstore.similarity_search_with_score(
        question,
        k=TOP_K
    )

    valid_docs = []

    for doc, score in results:
        # FAISS: score càng nhỏ càng giống
        if score <= SIMILARITY_THRESHOLD:
            valid_docs.append(doc)

    return valid_docs


def answer_question(question: str) -> dict:
    """
    Answer only if relevant context exists
    """

    docs = retrieve_context(question)

    # ❌ KHÔNG đủ ngữ cảnh → TỪ CHỐI
    if not docs:
        return {
            "answer": "Không tìm thấy thông tin phù hợp trong tài liệu.",
            "sources": []
        }

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
Bạn là AI trợ giảng.
Chỉ được sử dụng thông tin trong TÀI LIỆU bên dưới.
Nếu tài liệu không đủ thông tin để trả lời câu hỏi,
hãy trả lời đúng một câu:
"Không tìm thấy thông tin phù hợp trong tài liệu."

====================
TÀI LIỆU:
{context}
====================

CÂU HỎI:
{question}

TRẢ LỜI:
"""

    llm = get_llm()
    answer = llm.invoke(prompt)

    return {
        "answer": answer,
        "sources": docs
    }
