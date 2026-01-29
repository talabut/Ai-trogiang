import React, { useState } from 'react';
import api from '../api/client';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return alert("Chọn file!");
    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      await api.post('/upload/', formData, {
        params: { course_id: 'ML101' },
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert("Upload thành công!");
    } catch (error) {
      alert("Lỗi upload: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={loading}>Upload & Ingest</button>
    </div>
  );
};

export default FileUpload;