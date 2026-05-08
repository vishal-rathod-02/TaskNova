import axios from "axios";
import { useAuthStore } from "./stores/auth";

const api = axios.create({
  baseURL: "http://127.0.0.1:5000/api"
});

api.interceptors.request.use((config) => {
  const store = useAuthStore();
  if (store.accessToken) {
    config.headers.Authorization = `Bearer ${store.accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const store = useAuthStore();
    if (error.response?.status === 401 && store.refreshToken) {
      try {
        const res = await axios.post("http://127.0.0.1:5000/api/auth/refresh", null, {
          headers: {
            Authorization: `Bearer ${store.refreshToken}`
          }
        });
        store.setAccessToken(res.data.access_token);
        error.config.headers.Authorization = `Bearer ${store.accessToken}`;
        return api.request(error.config);
      } catch {
        store.logout();
      }
    }
    return Promise.reject(error);
  }
);

export default api;
