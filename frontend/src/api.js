// src/api.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const t = localStorage.getItem("access");
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

let refreshing = null;

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    // si 401 et pas déjà tenté un refresh
    if (error.response?.status === 401 && !original._retry) {
      if (!refreshing) {
        refreshing = (async () => {
          try {
            const refresh = localStorage.getItem("refresh");
            if (!refresh) throw new Error("no refresh");
            const r = await axios.post(
              ("http://127.0.0.1:8000/api") + "/token/refresh/",
              { refresh }
            );
            localStorage.setItem("access", r.data.access);
            return r.data.access;
          } finally {
            setTimeout(() => (refreshing = null), 0);
          }
        })();
      }
      const newAccess = await refreshing;
      original.headers.Authorization = `Bearer ${newAccess}`;
      original._retry = true;
      return api(original);
    }
    return Promise.reject(error);
  }
);

export default api;
