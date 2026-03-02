import { useState } from "react";

const InputBox = ({ onSend }) => {
  const [text, setText] = useState("");

  const handleSubmit = () => {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="input-box">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Nhập câu hỏi..."
      />
      <button onClick={handleSubmit}>Gửi</button>
    </div>
  );
};

export default InputBox;