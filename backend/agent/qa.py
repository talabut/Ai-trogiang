from typing import Dict, Any
from backend.rag.retrieval import hybrid_search

# --- CONFIGURATION ---
# Ngưỡng đã được xử lý bên trong hybrid_search (Source 133), 
# nhưng ta giữ check an toàn ở đây.
STRICT_REFUSAL_TEXT = "Tôi không tìm thấy thông tin phù hợp trong tài liệu được cung cấp."

def answer_question(question: str, course_id: str) -> Dict[str, Any]:
    """
    AI AGENT (STRICT – RETRIEVE ONLY)
    Logic:
    1. Retrieve via Hybrid Search (Vector + BM25).
    2. Refuse if empty.
    3. Return Context + Strict Citation.
    """
    
    # [cite_start]1. Retrieval (Hybrid) [cite: 134]
    # Tool duy nhất được phép sử dụng
    results = hybrid_search(query=question, course_id=course_id)
    
    # 2. Refusal Logic (Refuse if context empty)
    if not results:
        return {
            "answer": STRICT_REFUSAL_TEXT,
            "citations": []
        }

    # 3. Answer Construction (No LLM - Deterministic)
    # Ghép các đoạn context tìm được thành câu trả lời
    answers_text = []
    final_citations = []

    for item in results:
        # [cite_start]Extract Metadata [cite: 139]
        file_name = item.get("file_name", "Unknown")
        page = item.get("page", "N/A")
        line_start = item.get("line_start", "?")
        line_end = item.get("line_end", "?")
        score = item.get("final_score", 0.0)

        # Format Text Block
        chunk_text = item.get("text", "").strip()
        citation_line = f"(Nguồn: {file_name}, trang {page}, dòng {line_start}-{line_end})"
        
        # Combine Text + Citation
        answers_text.append(f"{chunk_text}\n{citation_line}")

        # Structure for Frontend
        final_citations.append({
            "doc_id": item.get("doc_id"),
            "file_name": file_name,
            "page": page,
            "line_start": line_start,
            "line_end": line_end,
            "score": round(score, 4)
        })

    # Join all chunks with double newline
    final_response = "\n\n".join(answers_text)

    return {
        "answer": final_response,
        "citations": final_citations
    }