import React, { useState } from 'react';
import api from '../api/client';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [courseId, setCourseId] = useState('ML101'); // Mặc định cho demo
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleUpload = async () => {
    if (!file) return alert('Vui lòng chọn file!');
    
    const formData = new FormData();
    formData.append('file', file);
    
    setLoading(true);
    setMessage('Đang xử lý tài liệu...');
    try {
      // Gọi đúng endpoint /api/upload/
      await api.post(`/upload/?course_id=${courseId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage('✅ Tải lên và Ingest thành công!');
    } catch (err) {
      setMessage('❌ Lỗi: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '15px', border: '1px solid #ddd', borderRadius: '8px', marginBottom: '20px' }}>
      <h3>1. Tải tài liệu (PDF/TXT)</h3>
      <input 
        type="text" 
        placeholder="Course ID" 
        value={courseId} 
        onChange={(e) => setCourseId(e.target.value)}
        style={{ marginBottom: '10px', display: 'block', padding: '5px' }}
      />
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={loading} style={{ marginLeft: '10px' }}>
        {loading ? 'Đang Ingest...' : 'Tải lên'}
      </button>
      {message && <p style={{ fontSize: '0.9em', marginTop: '10px' }}>{message}</p>}
    </div>
  );
};

export default FileUpload;