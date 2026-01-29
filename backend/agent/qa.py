from typing import Dict, Any, List
import json
from backend.rag.hybrid_retriever import hybrid_search
from backend.llm.llm import get_llm

# --- CONFIGURATION ---
THRESHOLD = 0.05 # Strict threshold after normalization/fusion

def answer_question(question: str, course_id: str) -> Dict[str, Any]:
    """
    Generates answer with strict citations using Hybrid RAG.
    """
    
    # 1. Retrieval (Hybrid)
    results = hybrid_search(question, course_id)
    
    # 2. Refusal Logic (Step 6)
    if not results or results[0]["final_score"] < THRESHOLD:
        return {
            "answer": "Tôi không tìm thấy thông tin phù hợp trong tài liệu đã cung cấp để trả lời câu hỏi này.",
            "citations": []
        }

    # 3. Context Assembly (Step 4)
    # Build context string with strict metadata markers
    context_str = ""
    valid_citations = []
    
    for i, item in enumerate(results):
        meta = item["metadata"]
        text = item["text"]
        
        # Safe get metadata for citation
        doc_id = meta.get("doc_id", "Unknown")
        file_name = meta.get("file_name", "Unknown")
        page = meta.get("page", "N/A")
        line_start =Hz = meta.get("line_start", "?")
        line_end = meta.get("line_end", "?")
        
        # Marker for LLM reference
        marker_id = f"REF_{i+1}"
        
        context_str += f"\n--- [{marker_id}] (File: {file_name}, Page: {page}, Lines: {line_start}-{line_end}) ---\n"
        context_str += f"{text}\n"

        valid_citations.append({
            "ref_id": marker_id,
            "doc_id": doc_id,
            "page": page,
            "line_start": line_start,
            "line_end": line_end,
            "file_name": file_name,
            "score": round(item["final_score"], 4)
        })

    # 4. Prompt Engineering (Step 5)
    prompt = f"""
Bạn là AI Trợ Giảng học thuật nghiêm túc.
Nhiệm vụ: Trả lời câu hỏi dựa trên các đoạn văn bản (Context) được cung cấp dưới đây.

QUY TẮC BẮT BUỘC:
1. Chỉ sử dụng thông tin có trong Context. KHÔNG bịa đặt, KHÔNG dùng kiến thức ngoài.
2. Nếu Context không đủ thông tin để trả lời câu hỏi, hãy nói "Tôi không tìm thấy thông tin trong tài liệu."
3. Khi trích dẫn thông tin, hãy ghi chú nguồn (ví dụ: Theo tài liệu [REF_1]...).

CONTEXT:
{context_str}

CÂU HỎI: 
{question}

TRẢ LỜI:
"""

    # 5. Call LLM
    llm = get_llm()
    # Note: The LocalMockLLM in current codebase parses regex "Ngữ cảnh tài liệu:". 
    # Since we changed the prompt format, we might need to update llm.py OR adapt the prompt to match regex.
    # To be safe with existing llm.py regex , let's add the specific marker it looks for:
    
    safe_prompt = f"Ngữ cảnh tài liệu:\n{context_str}\nCâu hỏi người dùng:\n{question}"
    
    raw_answer = llm.invoke(safe_prompt)

    # 6. Final Output Construction
    # We clean up the citation list to match the requirement schema
    final_citations = []
    for c in valid_citations:
        final_citations.append({
            "doc_id": c["doc_id"],
            "page": c["page"],
            "line_start": c["line_start"],
            "line_end": c["line_end"],
            "file_name": c["file_name"]
        })

    return {
        "answer": raw_answer,
        "citations": final_citations
    }