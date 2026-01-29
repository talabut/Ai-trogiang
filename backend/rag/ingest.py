import os
from pathlib import Path
from langchain_community.vectorstores import FAISS

from backend.vectorstore.faiss_store import get_faiss_store, embeddings_instance
from backend.utils.text_extraction import extract_text
from backend.utils.chunking import chunk_text
from backend.vectorstore.bm25_store import BM25Store

RAW_DOCS_DIR = "data/raw_docs"

def ingest_document(file_path: str, course_id: str):
    # 1. Generate Document ID & Filename
    file_name = os.path.basename(file_path)
    document_id = Path(file_path).stem
    
    print(f"📥 Starting Ingestion: {file_name} (ID: {document_id})")

    # 2. Extract Text -> Canonical Format (Page-delimited)
    canonical_content = extract_text(file_path, document_id)

    # 3. Persist Canonical TXT
    if not os.path.exists(RAW_DOCS_DIR):
        os.makedirs(RAW_DOCS_DIR)
        
    txt_path = os.path.join(RAW_DOCS_DIR, f"{document_id}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(canonical_content)

    # 4. Chunking (Dựa trên header trong canonical content)
    # chunk_text sẽ parse header để lấy metadata (page, ocr flag)
    docs = chunk_text(canonical_content, source_file=file_name)

    if not docs:
        print("⚠️ Warning: No chunks generated.")
        return

    # 5. Ingest FAISS
    index_path = os.path.join("data", "faiss_index", course_id)
    
    if os.path.exists(os.path.join(index_path, "index.faiss")):
        vector_store = FAISS.load_local(
            index_path, 
            embeddings_instance, 
            allow_dangerous_deserialization=True
        )
        vector_store.add_documents(docs)
    else:
        vector_store = FAISS.from_documents(docs, embeddings_instance)

    if not os.path.exists(os.path.dirname(index_path)):
        os.makedirs(os.path.dirname(index_path))
    
    vector_store.save_local(index_path)

    # 6. Ingest BM25
    bm25_store = BM25Store.load(course_id)
    bm25_store.add_documents(docs)
    bm25_store.save()

    print(f"✅ Ingest Complete: {len(docs)} chunks indexed for {course_id}")