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

      if (res.data.success) {
        setAnswer(res.data.data.answer);
      } else {
        setAnswer(res.data.error?.message || "No answer found.");
      }

    } catch (err) {
      setAnswer("System error. Please try again.");
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