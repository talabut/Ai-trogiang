import { useState } from "react";

export default function ChatBox() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      // FIX: URL phải khớp với router backend (main.py định nghĩa prefix="/chat") [cite: 5]
      const res = await fetch("http://localhost:8000/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          question,
          course_id: "ML101" // MVP: Fix cứng hoặc lấy từ state khóa học
        }),
      });
      const data = await res.json();
      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (err) {
      console.error("Lỗi:", err);
      setAnswer("Không thể kết nối đến server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto", padding: "20px", border: "1px solid #ddd" }}>
      <h3>Hỏi đáp tài liệu</h3>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={3}
        style={{ width: "100%", padding: "10px" }}
        placeholder="Nhập câu hỏi về bài học..."
      />
      <button onClick={ask} disabled={loading} style={{ marginTop: 10, padding: "10px 20px" }}>
        {loading ? "Đang suy nghĩ..." : "Gửi câu hỏi"}
      </button>

      {answer && (
        <div style={{ marginTop: 20, backgroundColor: "#f9f9f9", padding: "15px" }}>
          <strong>Trợ giảng AI:</strong>
          <p style={{ whiteSpace: "pre-wrap" }}>{answer}</p>
          
          {sources.length > 0 && (
            <div style={{ marginTop: 15, borderTop: "1px solid #eee", paddingTop: "10px" }}>
              <small>Nguồn tham khảo:</small>
              <ul style={{ fontSize: "0.85em" }}>
                {sources.map((s, idx) => (
                  <li key={idx}>
                    {s.source_file} {s.page ? `- Trang ${s.page}` : ""} 
                    <details>
                      <summary>Xem trích đoạn</summary>
                      <i>"...{s.content.substring(0, 200)}..."</i>
                    </details>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}