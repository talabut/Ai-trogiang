# FILE: backend/rag/chunking.py
import uuid
from typing import List, Dict, Any

# CẤU HÌNH SOFT RULES
MIN_CHUNK_CHARS = 300
MAX_CHUNK_CHARS = 800

def chunk_canonical_data(
    canonical_pages: List[Dict[str, Any]], 
    doc_id: str
) -> List[Dict[str, Any]]:
    """
    Tạo chunks từ dữ liệu Canonical tuân thủ Strict Page/Line Boundaries.
    
    Args:
        canonical_pages: Output từ bước canonicalize (List các Page objects).
        doc_id: ID của tài liệu gốc.

    Returns:
        List[Dict]: Danh sách chunks theo schema bắt buộc.
    """
    chunks = []

    # RULE 1: Duyệt theo từng Page (Không bao giờ vượt Page)
    for page_data in canonical_pages:
        page_num = page_data.get("page")
        lines = page_data.get("lines", [])
        
        if not lines:
            continue

        # Buffer cho chunk hiện tại
        current_buffer = []
        current_char_count = 0
        
        # Duyệt tuần tự các dòng trong trang
        for i, line in enumerate(lines):
            line_text = line.get("text", "")
            line_len = len(line_text)
            
            # Thêm dòng vào buffer tạm
            current_buffer.append(line)
            current_char_count += line_len
            
            # RULE 4 (Soft): Kiểm tra kích thước để ngắt chunk
            # Ngắt khi vượt quá MAX_CHUNK_CHARS hoặc là dòng cuối cùng của trang
            is_last_line = (i == len(lines) - 1)

            if (
                is_last_line
                or (
                    current_char_count >= MIN_CHUNK_CHARS
                    and (i + 1 < len(lines))
                    and (current_char_count + len(lines[i + 1].get("text", ""))) > MAX_CHUNK_CHARS
                )
            ):
                if current_buffer:
                    chunk_text = "\n".join([l["text"] for l in current_buffer])
                    
                    chunk_obj = {
                        "doc_id": doc_id,
                        "page": page_num,
                        "line_start": current_buffer[0]["line_id"],
                        "line_end": current_buffer[-1]["line_id"],
                        "text": chunk_text
                    }
                    
                    chunks.append(chunk_obj)
                
                current_buffer = []
                current_char_count = 0

    return chunks