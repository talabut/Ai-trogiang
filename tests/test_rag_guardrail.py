from backend.agent.qa import answer_question

def test_out_of_scope():
    r = answer_question("Ai là tổng thống Mỹ?")
    assert "không tìm thấy" in r["answer"].lower() \
        or "vượt ngoài phạm vi" in r["answer"].lower()
