import React, { useState } from 'react';
import api from '../api/client';

const ChatBox = () => {
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!query.trim()) return;

    const userMsg = { role: 'user', content: query };
    setChatHistory(prev => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      // Gọi đúng endpoint /api/chat/query
      const res = await api.post('/chat/query', {
        question: query,
        course_id: 'ML101' // Khớp với ID khi upload
      });

      const aiMsg = { role: 'ai', content: res.data.answer };
      setChatHistory(prev => [...prev, aiMsg]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'ai', content: 'Lỗi: Không thể kết nối với AI.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '15px', height: '400px', display: 'flex', flexDirection: 'column' }}>
      <h3>2. Chat với AI</h3>
      <div style={{ flex: 1, overflowY: 'auto', marginBottom: '10px', background: '#f9f9f9', padding: '10px' }}>
        {chatHistory.map((msg, i) => (
          <div key={i} style={{ marginBottom: '10px', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
            <span style={{ 
              background: msg.role === 'user' ? '#007bff' : '#eee', 
              color: msg.role === 'user' ? 'white' : 'black',
              padding: '5px 10px', borderRadius: '10px', display: 'inline-block'
            }}>
              {msg.content}
            </span>
          </div>
        ))}
        {loading && <p>AI đang suy nghĩ...</p>}
      </div>
      <div style={{ display: 'flex' }}>
        <input 
          style={{ flex: 1, padding: '10px' }} 
          value={query} 
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Hỏi gì đó về tài liệu..."
        />
        <button onClick={handleSend} style={{ padding: '10px 20px' }}>Gửi</button>
      </div>
    </div>
  );
};

export default ChatBox;