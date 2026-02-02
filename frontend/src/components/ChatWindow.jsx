import { useState } from "react";
import api from "../api/client";

export default function ChatWindow() {
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState("");

  async function send(question) {
    if (loading) return;
    setLoading(true);

    try {
      const res = await api.post("/chat", {
        question,
        session_id: "default"
      });
      setAnswer(res.data.data.answer);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <button onClick={() => send("Hello")} disabled={loading}>
        Ask
      </button>
      <div>{answer}</div>
    </div>
  );
}
