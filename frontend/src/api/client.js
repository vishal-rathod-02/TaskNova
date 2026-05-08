import axios from "axios";
import { useAuthStore } from "../stores/auth";

const apiClient = axios.create({
  baseURL: "http://127.0.0.1:5001/api",
});

apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore();
    if (error.response?.status === 401 && authStore.refreshToken) {
      try {
        await authStore.refreshAccessToken();
        error.config.headers.Authorization = `Bearer ${authStore.accessToken}`;
        return apiClient.request(error.config);
      } catch (refreshError) {
        authStore.logout();
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
