import os
import sys
from pathlib import Path

# Đảm bảo Python tìm thấy module backend
sys.path.append(str(Path(__file__).parent))

def setup_and_test():
    print("🚀 Bắt đầu kiểm tra hệ thống...")

    # 1. Tạo các thư mục cần thiết
    folders = ["data/faiss_index", "data/bm25", "uploads"]
    for f in folders:
        os.makedirs(f, exist_ok=True)
        print(f"✅ Đã tạo/kiểm tra thư mục: {f}")

    # 2. Tạo file dữ liệu mẫu để test
    sample_file = "uploads/test_knowledge.txt"
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write("Thủ đô của Việt Nam là Hà Nội. Khóa học ML101 dạy về Machine Learning cơ bản.")
    print(f"✅ Đã tạo file dữ liệu mẫu: {sample_file}")

    # 3. Test Ingest
    print("📥 Đang nạp dữ liệu vào Vector DB...")
    from backend.rag.ingest import ingest_document
    try:
        ingest_document(sample_file, "ML101")
        print("✅ Ingest thành công!")
    except Exception as e:
        print(f"❌ Lỗi Ingest: {e}")
        return

    # 4. Test Query
    print("🔍 Đang thử hỏi AI...")
    from backend.agent.qa import answer_question
    result = answer_question("Thủ đô của Việt Nam là gì?", "ML101")
    
    print("\n--- KẾT QUẢ TEST ---")
    print(f"Câu hỏi: Thủ đô của Việt Nam là gì?")
    print(f"AI trả lời: {result['answer']}")
    if result['sources']:
        print(f"Nguồn tìm thấy: {len(result['sources'])} đoạn văn.")
        print("🎉 HỆ THỐNG ĐÃ SẴN SÀNG!")
    else:
        print("⚠️ AI trả lời nhưng không tìm thấy nguồn. Kiểm tra lại hybrid_retriever.")

if __name__ == "__main__":
    setup_and_test()