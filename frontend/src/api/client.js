import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  timeout: 30000,
});

api.interceptors.response.use(
  r => r,
  async error => {
    const config = error.config;
    if (!config || config.__retry) return Promise.reject(error);

    config.__retry = true;
    return api(config);
  }
);

export default api;
