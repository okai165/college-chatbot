import axios from "axios";

const adminApi = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// attach token automatically
adminApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("admin_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default adminApi;