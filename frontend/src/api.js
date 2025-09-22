import axios from "axios";

const API_BASE = "http://127.0.0.1:8000"; // FastAPI সার্ভার URL

const api = axios.create({
  baseURL: API_BASE,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
