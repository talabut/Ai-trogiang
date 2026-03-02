import { useState } from "react";
import { uploadFile } from "../../api/upload";

const UploadPanel = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    try {
      await uploadFile(file, "ml_course");
      alert("Upload thành công!");
    } catch {
      alert("Upload thất bại!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Đang xử lý..." : "Upload"}
      </button>
    </div>
  );
};

export default UploadPanel;