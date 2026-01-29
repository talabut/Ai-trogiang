import json
import sys
import os

# Thêm đường dẫn để import được module backend
sys.path.append(os.getcwd())

from backend.rag.chunking import chunk_canonical_data

# 1. GIẢ LẬP INPUT (Canonical Structured TXT)
# Dữ liệu giả lập 2 trang, có dòng, có nội dung liền mạch
mock_canonical_input = [
    {
        "page": 1,
        "source": "manual_upload",
        "lines": [
            {"line_id": 1, "text": "CHƯƠNG 1: GIỚI THIỆU VỀ MACHINE LEARNING"},
            {"line_id": 2, "text": "Học máy (Machine Learning) là một lĩnh vực của trí tuệ nhân tạo."},
            {"line_id": 3, "text": "Nó tập trung vào việc xây dựng các hệ thống có khả năng học hỏi từ dữ liệu."},
            {"line_id": 4, "text": "Thay vì lập trình các quy tắc cụ thể, chúng ta huấn luyện mô hình."},
            {"line_id": 5, "text": "Mô hình sẽ tự tìm ra các quy luật ẩn chứa bên trong dữ liệu đầu vào."},
            {"line_id": 6, "text": "Có ba loại học máy chính: Học có giám sát, không giám sát và bán giám sát."},
            {"line_id": 7, "text": "Trong học có giám sát, dữ liệu được dán nhãn cụ thể."},
            {"line_id": 8, "text": "Ví dụ: Phân loại email là spam hay không spam dựa trên lịch sử."},
            {"line_id": 9, "text": "Học không giám sát xử lý dữ liệu chưa được dán nhãn."},
            {"line_id": 10, "text": "Mục tiêu là tìm ra cấu trúc ẩn, ví dụ như gom nhóm khách hàng."}
        ]
    },
    {
        "page": 2,
        "source": "manual_upload",
        "lines": [
            {"line_id": 1, "text": "CHƯƠNG 2: MẠNG NƠ-RON NHÂN TẠO"},
            {"line_id": 2, "text": "Mạng nơ-ron được lấy cảm hứng từ bộ não con người."},
            {"line_id": 3, "text": "Nó bao gồm các lớp: Lớp đầu vào, lớp ẩn và lớp đầu ra."},
            {"line_id": 4, "text": "Mỗi nơ-ron nhận tín hiệu, nhân trọng số và đi qua hàm kích hoạt."},
            {"line_id": 5, "text": "Deep Learning là thuật ngữ chỉ các mạng nơ-ron có nhiều lớp ẩn."},
            {"line_id": 6, "text": "Ứng dụng của Deep Learning bao gồm nhận diện ảnh và xử lý ngôn ngữ."}
        ]
    }
]

def run_test():
    doc_id = "DOC_TEST_001"
    
    # 2. CHẠY LOGIC CHUNKING
    print("⏳ Đang thực hiện Chunking...")
    chunks = chunk_canonical_data(mock_canonical_input, doc_id)
    
    # 3. XUẤT OUTPUT RA JSONL
    output_file = "chunks_output.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            
    print(f"✅ Đã tạo file output: {output_file}")
    print(f"📊 Tổng số chunks: {len(chunks)}")
    
    # In mẫu để kiểm tra
    print("\n--- MẪU 2 CHUNKS ĐẦU TIÊN ---")
    for c in chunks[:2]:
        print(json.dumps(c, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run_test()