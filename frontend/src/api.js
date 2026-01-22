import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000"
});

export function setToken(token) {
  api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
}
