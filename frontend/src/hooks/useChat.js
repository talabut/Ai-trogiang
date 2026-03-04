import { useState } from "react";

import { sendMessage } from "../api/chat";

const REASON_MESSAGE = {
  NO_MATCH: "Tài liệu không đề cập trực tiếp nội dung câu hỏi.",
  WEAK_EVIDENCE:
    "Tài liệu có đề cập gián tiếp nhưng không đủ bằng chứng học thuật để trả lời.",
  OUT_OF_SCOPE: "Câu hỏi nằm ngoài phạm vi nội dung tài liệu đã nạp.",
};

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

      if (!res?.success) {
        const reason = res?.reason || "WEAK_EVIDENCE";
        const retrievalStats = res?.retrieval_stats || {
          nodes_found: 0,
          max_score: 0,
        };

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            type: "refusal",
            reason,
            retrievalStats,
            content: res?.message || REASON_MESSAGE[reason] || REASON_MESSAGE.WEAK_EVIDENCE,
            sources: [],
            evidenceCount: 0,
          },
        ]);
        return;
      }

      const botMsg = {
        role: "assistant",
        type: "answer",
        content: res.data.answer,
        sources: res.data.sources,
        evidenceCount: res.data.evidence_count,
        reason: res.data.reason,
        retrievalStats: res.data.retrieval_stats,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          type: "error",
          content: "Lỗi backend: " + err.message,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return { messages, ask, loading };
};
