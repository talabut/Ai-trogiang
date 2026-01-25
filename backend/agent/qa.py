from typing import Dict, Any, List, Tuple
from langchain_core.documents import Document

from backend.rag.hybrid_retriever import hybrid_search
from backend.llm.llm import get_llm
from backend.utils.citation import format_apa, format_ieee


TOP_K = 5
HYBRID_THRESHOLD = 0.15

WATERMARK = (
    "\n\n— AI Trợ Giảng\n"
    "Nội dung này được tạo tự động dựa trên tài liệu học tập nội bộ. "
    "Không thay thế tài liệu chính thức."
)


def answer_question(question: str) -> Dict[str, Any]:
    """
    Answer question using Hybrid Search with strict academic guardrails.

    Guardrails:
    - No retrieval → refuse
    - Low-score retrieval → refuse
    - LLM is NEVER called without grounded context
    """

    # === BASIC INPUT CHECK ===
    if not question or len(question.strip()) < 5:
        return {
            "answer": "Câu hỏi không hợp lệ hoặc quá ngắn.",
            "sources": [],
            "citations": {"apa": [], "ieee": []}
        }

    # === RETRIEVAL ===
    results: List[Tuple[Document, float]] = hybrid_search(question)

    # === GUARD 1: NO DOCUMENT FOUND ===
    if not results:
        return {
            "answer": "Tôi không tìm thấy thông tin trong tài liệu đã được cung cấp.",
            "sources": [],
            "citations": {"apa": [], "ieee": []}
        }

    # === APPLY THRESHOLD ===
    filtered: List[Tuple[Document, float]] = [
        (doc, score)
        for doc, score in results[:TOP_K]
        if score >= HYBRID_THRESHOLD
    ]

    # === GUARD 2: OUT-OF-SCOPE QUESTION ===
    if not filtered:
        return {
            "answer": (
                "Câu hỏi này vượt ngoài phạm vi các tài liệu hiện có. "
                "Tôi không đủ căn cứ học thuật để trả lời."
            ),
            "sources": [],
            "citations": {"apa": [], "ieee": []}
        }

    # === BUILD CONTEXT & SOURCES ===
    sources = []
    context_parts = []

    for idx, (doc, score) in enumerate(filtered):
        sources.append({
            "source_file": doc.metadata.get("source_file"),
            "page": doc.metadata.get("page"),
            "section": doc.metadata.get("section"),
            "chunk_id": doc.metadata.get("chunk_id"),
            "score": round(score, 4),
            "preview": doc.page_content[:200]
        })

        context_parts.append(
            f"[CHUNK_{doc.metadata.get('chunk_id')}]\n{doc.page_content}"
        )

    context = "\n\n".join(context_parts)

    # === PROMPT (STRICT GROUNDED) ===
    prompt = f"""
Bạn là AI Trợ Giảng học thuật.

CHỈ sử dụng thông tin trong các CHUNK bên dưới.
Mỗi ý trả lời PHẢI kết thúc bằng tag [CHUNK_x] tương ứng.
Nếu không đủ thông tin → từ chối trả lời.

TÀI LIỆU:
{context}

CÂU HỎI:
{question}

TRẢ LỜI:
"""

    # === CALL LLM (SAFE POINT) ===
    llm = get_llm()
    answer = llm.invoke(prompt).strip() + WATERMARK

    citations = {
        "apa": [format_apa(s) for s in sources],
        "ieee": [format_ieee(s, i + 1) for i, s in enumerate(sources)]
    }

    return {
        "answer": answer,
        "sources": sources,
        "citations": citations
    }
