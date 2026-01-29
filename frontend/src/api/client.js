import axios from "axios";

// Khởi tạo axios instance cơ bản nhất
export const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});
export default api;
// KHÔNG thêm bất kỳ interceptors nào liên quan đến Authorization ở đây