import { useState } from "react";

export default function ChatBox() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [citations, setCitations] = useState(null);

  const ask = async () => {
    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();
    setAnswer(data.answer);
    setSources(data.sources || []);
    setCitations(data.citations || null);
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto" }}>
      <h2>AI Trợ Giảng</h2>

      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={3}
        style={{ width: "100%" }}
      />

      <button onClick={ask} style={{ marginTop: 10 }}>
        Hỏi
      </button>

      {answer && (
        <>
          <h3>Trả lời (có gắn nguồn)</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{answer}</pre>
        </>
      )}

      {sources.length > 0 && (
        <>
          <h4>Nguồn tham khảo theo Chunk</h4>
          <ul>
            {sources.map((s, idx) => (
              <li key={idx}>
                <b>[CHUNK_{idx}]</b> — {s.source_file}
                {s.page !== null && ` – Trang ${s.page}`}
                {s.section && ` – ${s.section}`}
                <details>
                  <summary>Xem trích đoạn</summary>
                  <small>{s.preview}</small>
                </details>
              </li>
            ))}
          </ul>
        </>
      )}

      {citations && (
        <>
          <h4>References (APA)</h4>
          <ul>
            {citations.apa.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>

          <h4>References (IEEE)</h4>
          <ul>
            {citations.ieee.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
