from typing import Dict, Any, List
from langchain.schema import Document

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
    Answer question using Hybrid Search (FAISS + BM25)
    with strict threshold, citation, traceability, audit-ready
    """

    results = hybrid_search(question)

    if not results:
        return {
            "answer": "Tôi không tìm thấy thông tin phù hợp trong tài liệu đã cung cấp.",
            "sources": [],
            "citations": {"apa": [], "ieee": []}
        }

    # --- Apply hybrid threshold ---
    filtered: List[tuple[Document, float]] = [
        (doc, score)
        for doc, score in results[:TOP_K]
        if score >= HYBRID_THRESHOLD
    ]

    if not filtered:
        return {
            "answer": (
                "Tôi không đủ thông tin từ tài liệu hiện có để trả lời câu hỏi này. "
                "Vui lòng tham khảo thêm tài liệu hoặc hỏi lại với nội dung cụ thể hơn."
            ),
            "sources": [],
            "citations": {"apa": [], "ieee": []}
        }

    # --- Build sources ---
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
            f"[CHUNK_{idx}]\n{doc.page_content}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
Bạn là AI Trợ Giảng.

CHỈ sử dụng thông tin trong các CHUNK bên dưới.
Mỗi ý chính PHẢI kết thúc bằng tag [CHUNK_x] tương ứng.
Nếu không đủ thông tin từ các CHUNK, hãy từ chối trả lời.

TÀI LIỆU:
{context}

CÂU HỎI:
{question}

TRẢ LỜI:
"""

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
