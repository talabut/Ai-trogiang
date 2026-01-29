// FILE: frontend/src/App.jsx
import React from "react";
import FileUpload from "./components/FileUpload";
import ChatBox from "./components/ChatBox";

export default function App() {
  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "20px", fontFamily: "Arial" }}>
      <h1 style={{ textAlign: "center", color: "#2c3e50" }}>
        AI Trợ Giảng (Demo No Auth)
      </h1>
      
      {/* 1. Khu vực Upload (Luôn hiển thị) */}
      <section style={{ 
        marginBottom: "30px", padding: "20px", 
        border: "1px solid #ddd", borderRadius: "8px", 
        backgroundColor: "#f9f9f9" 
      }}>
        <FileUpload />
      </section>

      {/* 2. Khu vực Chat (Luôn hiển thị) */}
      <section>
        <ChatBox />
      </section>
    </div>
  );
}