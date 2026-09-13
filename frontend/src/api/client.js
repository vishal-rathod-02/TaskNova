import axios from "axios";
import { useAuthStore } from "../stores/auth";

const getBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:5001";
  const trimmed = envUrl.trim().replace(/\/+$/, "");
  return trimmed.endsWith("/api") ? trimmed : `${trimmed}/api`;
};

const apiClient = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
});

const isRefreshRequest = (config) => config?.url?.includes("/auth/refresh");
const isPublicAuthRequest = (config) =>
  config?.url?.includes("/auth/login") || config?.url?.includes("/auth/register");

apiClient.interceptors.request.use((config) => {
  if (isRefreshRequest(config)) {
    return config;
  }
  const authStore = useAuthStore();
  if (authStore.accessToken && !config.headers?.Authorization) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore();
    const originalRequest = error.config;

    if (isRefreshRequest(originalRequest) || isPublicAuthRequest(originalRequest)) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        authStore.logout();
      }
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && authStore.refreshToken && !originalRequest?._retry) {
      try {
        originalRequest._retry = true;
        await authStore.refreshAccessToken();
        originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`;
        return apiClient.request(originalRequest);
      } catch (refreshError) {
        authStore.logout();
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
