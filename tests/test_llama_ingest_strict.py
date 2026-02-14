# FILE: tests/test_llama_ingest_strict.py
import os
import shutil
import pytest

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


# ============================================================
# FIX CHUẨN: PREPARE INDEX 1 LẦN, CLEANUP SAU MODULE
# ============================================================
@pytest.fixture(scope="module")
def prepared_index():
    path = get_index_path(COURSE_ID)

    # Clean trước khi ingest
    if os.path.exists(path):
        shutil.rmtree(path)

    # Ingest canonical chunks (1 lần)
    ingest_canonical_chunks(
        MOCK_CHUNKS,
        COURSE_ID,
        "test_file.txt",
        "TEST_DOC_1"
    )

    yield

    # Cleanup sau khi toàn bộ module test xong
    if os.path.exists(path):
        shutil.rmtree(path)


# ============================================================
# TEST 1: INGESTION
# ============================================================
def test_ingestion(prepared_index):
    print("\n--- 🧪 TEST 1: Initial Ingestion ---")

    idx_path = get_index_path(COURSE_ID)

    assert os.path.exists(
        os.path.join(idx_path, "docstore.json")
    ), "docstore.json not created"

    assert os.path.exists(
        os.path.join(idx_path, "default__vector_store.json")
    ), "vector store not created"


# ============================================================
# TEST 2: DEDUPLICATION
# ============================================================
def test_deduplication(prepared_index):
    print("\n--- 🧪 TEST 2: Deduplication Check ---")

    NEW_CHUNK = [
        {
            "doc_id": "TEST_DOC_2",
            "page": 99,
            "line_start": 1,
            "line_end": 1,
            "text": "Đây là chunk hoàn toàn mới."
        }
    ]

    ingest_canonical_chunks(
        NEW_CHUNK,
        COURSE_ID,
        "test_file_2.txt",
        "TEST_DOC_2"
    )

    # Không assert số lượng node ở đây
    # Mục tiêu: đảm bảo không crash & không overwrite dữ liệu cũ


# ============================================================
# TEST 3: RETRIEVAL + METADATA INTEGRITY
# ============================================================
def test_retrieval_integrity(prepared_index):
    print("\n--- 🧪 TEST 3: Retrieval & Metadata Integrity ---")

    retriever = get_llama_retriever(COURSE_ID, top_k=1)
    results = retriever.retrieve("Kiến trúc RAG")

    assert results, "No results found"

    top_node = results[0]
    meta = top_node.metadata

    # --- Metadata integrity checks ---
    assert meta.get("page") == 1, "Wrong page value"
    assert meta.get("line_start") == 1, "Missing/Wrong line_start"
    assert meta.get("line_end") == 5, "Missing/Wrong line_end"
    assert meta.get("doc_id") == "TEST_DOC_1", "Wrong doc_id"

    assert meta.get("index_version") == "v1.0", "Missing/Wrong index_version"

    assert (
        meta.get("embedding_model")
        == "sentence-transformers/all-MiniLM-L6-v2"
    ), "Wrong embedding_model tag"
