from backend.rag.hybrid_retriever import hybrid_search
from backend.agent.qa import answer_question

def test_empty_query():
    assert hybrid_search("") == []

def test_short_query():
    assert hybrid_search("hi") == []

def test_out_of_scope_question():
    result = answer_question("Thủ đô của Pháp là gì?")
    assert "không tìm thấy" in result["answer"].lower() \
        or "vượt ngoài phạm vi" in result["answer"].lower()
