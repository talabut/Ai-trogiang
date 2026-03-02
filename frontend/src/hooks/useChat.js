import { useState } from "react";
import { sendMessage } from "../api/chat";
export const useChat = (courseId, sessionId) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const ask = async (text) => {
    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);

    setLoading(true);

    try {
      const res = await sendMessage({
        course_id: courseId,
        session_id: sessionId,
        question: text,
      });

      const botMsg = {
        role: "assistant",
        content: res.data.answer,
        sources: res.data.sources,
        evidenceCount: res.data.evidence_count,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Lỗi backend: " + err.message,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return { messages, ask, loading };
};