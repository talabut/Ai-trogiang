import { useState } from "react";
import { api, setToken } from "./api";
import ChatBox from "./components/ChatBox";

export default function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState(null);
  const [file, setFile] = useState(null);

  async function login() {
    const res = await api.post("/auth/login", {
      username,
      password,
    });

    setToken(res.data.access_token);
    setRole(res.data.role);

    alert("Login thành công với role: " + res.data.role);
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

      {/* LOGIN */}
      <h3>Login</h3>
      <input
        placeholder="username"
        onChange={(e) => setUsername(e.target.value)}
      />
      <br />
      <input
        type="password"
        placeholder="password"
        onChange={(e) => setPassword(e.target.value)}
      />
      <br />
      <button onClick={login}>Login</button>

      {/* UPLOAD – TEACHER ONLY */}
      {role === "teacher" && (
        <>
          <h3>Upload tài liệu (GV)</h3>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <br />
          <button onClick={upload}>Upload</button>
        </>
      )}

      <hr />

      {/* CHAT – DÙNG CHATBOX PHASE 3 */}
      <ChatBox />
    </div>
  );
}
