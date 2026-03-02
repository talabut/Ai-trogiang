import Sidebar from "./components/layout/Sidebar";
import ChatWindow from "./components/chat/ChatWindow";

function App() {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <Sidebar />
      <ChatWindow />
    </div>
  );
}

export default App;