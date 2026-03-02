const ChatLayout = ({ children }) => {
  return (
    <div className="layout">
      <div className="sidebar">
        <h2>AI Trợ Giảng</h2>
      </div>

      <div className="chat-area">
        {children}
      </div>
    </div>
  );
};

export default ChatLayout;