from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_chat_response_contract():
    res = client.post("/api/v1/chat", json={
        "question": "hello",
        "session_id": "test"
    })
    body = res.json()

    assert "success" in body
    assert body["success"] is True
    assert "data" in body
    assert "answer" in body["data"]
