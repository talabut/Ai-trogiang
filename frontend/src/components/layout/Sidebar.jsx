import { useEffect, useState } from "react";
import { checkHealth } from "../../api/health";
import UploadPanel from "../upload/UploadPanel";

const Sidebar = () => {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    checkHealth()
      .then(() => setStatus("online"))
      .catch(() => setStatus("offline"));
  }, []);

  return (
    <div className="sidebar">
      <h2>AI Trợ Giảng</h2>
      <div className={`health ${status}`}>
        Backend: {status}
      </div>
      <UploadPanel />
    </div>
  );
};

export default Sidebar;