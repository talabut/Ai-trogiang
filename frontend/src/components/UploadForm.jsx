import React, { useState } from 'react';
import { uploadFile } from '../api/upload';

const COURSE_ID = 'default_course';

const UploadForm = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState(null);

  const handleUpload = async () => {
    if (!file || uploading) return;

    setUploading(true);
    setProgress(0);
    setStatus(null);

    try {
      await uploadFile(COURSE_ID, file, setProgress);
      setStatus({ type: 'success', text: 'Upload successful' });
      setFile(null);
    } catch (err) {
      setStatus({
        type: 'error',
        text:
          err.userMessage ||
          err.response?.data?.error?.message ||
          'Upload failed',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-form">
      <input
        type="file"
        disabled={uploading}
        onChange={(e) => setFile(e.target.files[0])}
      />

      {uploading && (
        <div className="progress">
          <div style={{ width: `${progress}%` }} />
          <span>{progress}%</span>
        </div>
      )}

      <button disabled={!file || uploading} onClick={handleUpload}>
        {uploading ? 'Uploading…' : 'Upload'}
      </button>

      {status && (
        <div className={`status ${status.type}`}>
          {status.text}
        </div>
      )}
    </div>
  );
};

export default UploadForm;
