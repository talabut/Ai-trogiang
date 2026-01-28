import React from 'react';
import FileUpload from './components/FileUpload';
import ChatBox from './components/ChatBox';

function App() {
  // KHÔNG thêm logic kiểm tra isAuth hay Redirect ở đây
  return (
    <div style={{ 
      maxWidth: '900px', 
      margin: '40px auto', 
      padding: '0 20px',
      fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif' 
    }}>
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ color: '#2c3e50' }}>AI Teaching Assistant - MVP</h1>
        <p>Tải tài liệu lên và bắt đầu đặt câu hỏi</p>
      </header>

      <main>
        <FileUpload />
        <ChatBox />
      </main>

      <footer style={{ marginTop: '50px', textAlign: 'center', color: '#888', fontSize: '0.8em' }}>
        Chế độ Demo: Không yêu cầu đăng nhập.
      </footer>
    </div>
  );
}

export default App;