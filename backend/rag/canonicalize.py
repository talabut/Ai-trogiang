from typing import List, Dict, Any

def canonicalize_pages(extracted_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Chuyển đổi dữ liệu thô từ PDF/OCR thành Canonical Structured Data.
    
    Quy tắc:
    - Input: List[{page, text, source}]
    - Output: List[{page, source, lines: [{line_id, text}]}]
    - Xử lý: Tách dòng, clean whitespace, đánh số line_id nội bộ theo trang.
    
    Args:
        extracted_pages (List[Dict]): Dữ liệu từ bước PDF->TXT.

    Returns:
        List[Dict]: Cấu trúc dữ liệu chuẩn hóa theo dòng.
    """
    # 1. Đảm bảo đúng thứ tự trang (tăng dần)
    sorted_pages = sorted(extracted_pages, key=lambda x: x.get("page", 0))
    
    canonical_data = []

    for page_data in sorted_pages:
        page_num = page_data.get("page", 0)
        source = page_data.get("source", "unknown")
        raw_text = page_data.get("text", "") or ""

        clean_lines_list = []
        line_counter = 1
        
        # Tách dòng dựa trên ký tự newline
        raw_lines = raw_text.splitlines()
        
        for line in raw_lines:
            # 2. Clean text: Strip whitespace đầu/cuối
            clean_content = line.strip()
            
            # 3. Bỏ dòng rỗng hoàn toàn
            if not clean_content:
                continue
                
            # 4. Tạo Line Object
            clean_lines_list.append({
                "line_id": line_counter,
                "text": clean_content
            })
            line_counter += 1

        # Tạo Page Object hoàn chỉnh
        page_structure = {
            "page": page_num,
            "source": source,
            "lines": clean_lines_list
        }
        
        canonical_data.append(page_structure)

    return canonical_data