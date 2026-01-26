import React, { useState } from "react";
import axios from "axios";

function FileUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [courseId, setCourseId] = useState("ML101");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Vui lòng chọn một file!");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    // Quan trọng: Tên 'file' phải khớp với backend
    formData.append("file", selectedFile);

    try {
      const response = await axios.post(
        `http://localhost:8000/upload/?course_id=${courseId}`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      alert("Upload thành công: " + response.data.message);
    } catch (error) {
      console.error("Lỗi upload:", error);
      alert("Lỗi upload: " + (error.response?.data?.detail || "Không rõ lỗi"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", border: "1px solid #ccc", marginBottom: "20px" }}>
      <h3>Upload Tài Liệu (GV)</h3>
      <input
        type="text"
        placeholder="Course ID (vd: ML101)"
        value={courseId}
        onChange={(e) => setCourseId(e.target.value)}
      />
      <br /><br />
      <input type="file" onChange={handleFileChange} accept=".txt" />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Đang xử lý..." : "Tải lên & Ingest"}
      </button>
    </div>
  );
}

export default FileUpload;