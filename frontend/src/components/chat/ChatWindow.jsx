import { useState } from "react";
import { useChat } from "../../hooks/useChat";
import MessageBubble from "./MessageBubble";
import InputBox from "./InputBox";

const ChatWindow = () => {
  const [courseId, setCourseId] = useState("ml_course");
  const [sessionId, setSessionId] = useState("session_1");

  const { messages, ask, loading } = useChat(courseId, sessionId);

  return (
    <div className="chat-window">
      <div className="chat-controls">
        <input
          value={courseId}
          onChange={(e) => setCourseId(e.target.value)}
          placeholder="Course ID"
        />
        <input
          value={sessionId}
          onChange={(e) => setSessionId(e.target.value)}
          placeholder="Session ID"
        />
      </div>

      <div className="messages">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}

        {loading && (
          <div className="bubble assistant">AI đang xử lý...</div>
        )}
      </div>

      <InputBox onSend={ask} />
    </div>
  );
};

export default ChatWindow;