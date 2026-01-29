# FILE: tests/test_llama_ingest_strict.py
import sys
import os
import shutil
import json

# Add project root to path
sys.path.append(os.getcwd())

from backend.rag.llama_ingest import ingest_canonical_chunks, get_index_path
from backend.rag.retrieval import get_llama_retriever

# --- MOCK DATA ---
MOCK_CHUNKS = [
    {
        "doc_id": "TEST_DOC_1",
        "page": 1,
        "line_start": 1,
        "line_end": 5,
        "text": "Kiến trúc RAG bao gồm Retrieval và Generation. Đây là test chunk số 1."
    },
    {
        "doc_id": "TEST_DOC_1",
        "page": 1,
        "line_start": 6,
        "line_end": 10,
        "text": "LlamaIndex giúp quản lý dữ liệu cho LLM. Đây là test chunk số 2."
    },
    {
        "doc_id": "TEST_DOC_1",
        "page": 2,
        "line_start": 1,
        "line_end": 4,
        "text": "Embedding model chuyển text thành vector. Đây là test chunk số 3."
    }
]

COURSE_ID = "TEST_COURSE_V1"

def clean_test_env():
    path = get_index_path(COURSE_ID)
    if os.path.exists(path):
        shutil.rmtree(path)
    print(f"🧹 Cleaned test environment: {path}")

def test_ingestion():
    print("\n--- 🧪 TEST 1: Initial Ingestion ---")
    
    # 1. First Ingest
    ingest_canonical_chunks(MOCK_CHUNKS, COURSE_ID, "test_file.txt", "TEST_DOC_1")
    
    # Check if files exist
    idx_path = get_index_path(COURSE_ID)
    if os.path.exists(os.path.join(idx_path, "docstore.json")) and \
       os.path.exists(os.path.join(idx_path, "default__vector_store.json")):
        print("✅ Storage files created.")
    else:
        print("❌ Storage files MISSING.")
        return False
    return True

def test_deduplication():
    print("\n--- 🧪 TEST 2: Deduplication Check ---")
    
    # 2. Re-ingest same chunks (Expect skipping all)
    print("running re-ingest (should skip all)...")
    ingest_canonical_chunks(MOCK_CHUNKS, COURSE_ID, "test_file.txt", "TEST_DOC_1")
    
    # 3. Ingest new chunk
    NEW_CHUNK = [{
        "doc_id": "TEST_DOC_2", 
        "page": 99, 
        "line_start": 1, 
        "line_end": 1, 
        "text": "Đây là chunk hoàn toàn mới."
    }]
    print("running ingest new chunk...")
    ingest_canonical_chunks(NEW_CHUNK, COURSE_ID, "test_file_2.txt", "TEST_DOC_2")
    
    print("✅ Deduplication logic executed (check logs for 'Skipped' messages).")

def test_retrieval_integrity():
    print("\n--- 🧪 TEST 3: Retrieval & Metadata Integrity ---")
    
    retriever = get_llama_retriever(COURSE_ID, top_k=1)
    results = retriever.retrieve("Kiến trúc RAG")
    
    if not results:
        print("❌ No results found!")
        return

    top_node = results[0]
    meta = top_node.metadata
    
    print("🔍 Retrieved Node Metadata:")
    print(json.dumps(meta, indent=2))
    
    # Strict Validation Checks
    checks = [
        ("page" in meta, "Missing 'page'"),
        (meta.get("page") == 1, "Wrong 'page' value"),
        ("line_start" in meta, "Missing 'line_start'"),
        ("line_end" in meta, "Missing 'line_end'"),
        (meta.get("doc_id") == "TEST_DOC_1", "Wrong 'doc_id'"),
        (meta.get("index_version") == "v1.0", "Missing/Wrong version"),
        (meta.get("embedding_model") == "sentence-transformers/all-MiniLM-L6-v2", "Wrong Embedding Tag")
    ]
    
    passed = True
    for condition, msg in checks:
        if not condition:
            print(f"❌ FAIL: {msg}")
            passed = False
    
    if passed:
        print("✅ All Metadata checks PASSED.")

def main():
    clean_test_env()
    if test_ingestion():
        test_deduplication()
        test_retrieval_integrity()
    
    print("\n🎉 ALL TESTS COMPLETED.")

if __name__ == "__main__":
    main()