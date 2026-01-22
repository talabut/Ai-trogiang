import { useState } from "react";
import { api, setToken } from "./api";

export default function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [file, setFile] = useState(null);

  async function login() {
    const res = await api.post("/auth/login", { username, password });
    setToken(res.data.access_token);
    setRole(res.data.role);
    alert("Login thành công với role: " + res.data.role);
  }

  async function ask() {
    const res = await api.post("/chat", { question });
    setAnswer(res.data.answer);
  }

  async function upload() {
    const form = new FormData();
    form.append("file", file);
    await api.post("/upload/", form);
    alert("Upload & ingest xong");
  }

  return (
    <div style={{ padding: 30, fontFamily: "Arial" }}>
      <h2>AI Trợ Giảng</h2>

      <h3>Login</h3>
      <input placeholder="username" onChange={e => setUsername(e.target.value)} />
      <input type="password" placeholder="password" onChange={e => setPassword(e.target.value)} />
      <button onClick={login}>Login</button>

      {role === "teacher" && (
        <>
          <h3>Upload tài liệu (GV)</h3>
          <input type="file" onChange={e => setFile(e.target.files[0])} />
          <button onClick={upload}>Upload</button>
        </>
      )}

      <h3>Chat</h3>
      <input
        style={{ width: "400px" }}
        placeholder="Nhập câu hỏi"
        onChange={e => setQuestion(e.target.value)}
      />
      <button onClick={ask}>Hỏi</button>

      <p><b>Trả lời:</b> {answer}</p>
    </div>
  );
}
