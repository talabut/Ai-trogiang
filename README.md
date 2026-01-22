# AI Trợ Giảng (RAG-based Tutor Assistant)

Dự án AI trợ giảng sử dụng kiến trúc **RAG (Retrieval-Augmented Generation)**:
- Ingest tài liệu học tập (TXT / PDF / DOCX)
- Lưu vector bằng FAISS
- Trả lời câu hỏi dựa trên tài liệu (không bịa)

---

## 1. Cấu trúc dự án

backend/
agent/ # AI tutor logic
rag/ # ingest + retriever
api/ # FastAPI endpoints
main.py
data/
raw_docs/ # tài liệu đầu vào (GV upload)
faiss_index/ # vector database


---

## 2. Cài đặt môi trường

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
