import axios from 'axios';

const api = axios.create({
  // Base URL trỏ đến Backend FastAPI
  baseURL: 'http://localhost:8000/api',
});

// Không sử dụng interceptors cho token để tránh lỗi khi không có login
export default api;