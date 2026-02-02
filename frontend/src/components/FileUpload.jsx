import { useState } from "react";
import { uploadFile } from "../api/upload";

export default function FileUpload() {
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setError(null);
      await uploadFile(file, setProgress);
    } catch (err) {
      setError("Upload failed");
    }
  }

  return (
    <div>
      <input type="file" onChange={handleUpload} />
      {progress > 0 && <div>Uploading: {progress}%</div>}
      {error && <div style={{color:"red"}}>{error}</div>}
    </div>
  );
}
