// FILE: frontend/src/components/ChatBox.jsx
import React, { useState } from 'react';
import { api } from '../api/client'; // Hoặc import axios trực tiếp nếu chưa config api

const ChatBox = () => {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");

    try {
      // FIX: Gọi đúng POST /chat/query
      // Đảm bảo baseURL là http://localhost:8000
      const res = await api.post("/chat/query", {
        question: question,
        course_id: "ML101" 
      });

      setAnswer(res.data.answer);
    } catch (err) {
      console.error(err);
      setAnswer("Lỗi kết nối server!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ border: "1px solid #ccc", padding: "20px", borderRadius: "8px" }}>
      <h3>Hỏi đáp AI</h3>
      <textarea 
        style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
        rows={3}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Nhập câu hỏi..."
      />
      <button onClick={handleSend} disabled={loading} style={{ padding: "10px 20px" }}>
        {loading ? "Đang suy nghĩ..." : "Gửi câu hỏi"}
      </button>
      
      {answer && (
        <div style={{ marginTop: "20px", padding: "10px", background: "#eef" }}>
          <strong>Trả lời:</strong>
          <p style={{ whiteSpace: "pre-wrap" }}>{answer}</p>
        </div>
      )}
    </div>
  );
};

export default ChatBox;