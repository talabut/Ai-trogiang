import { useState } from "react";
import Sidebar from "./components/layout/Sidebar";
import ChatWindow from "./components/chat/ChatWindow";

function App() {
  const [courseId, setCourseId] = useState("ml_course");

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <Sidebar courseId={courseId} />
      <ChatWindow courseId={courseId} setCourseId={setCourseId} />
    </div>
  );
}

export default App;
