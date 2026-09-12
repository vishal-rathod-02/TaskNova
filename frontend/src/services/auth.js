import apiClient from "../api/client";

export const registerUser = (payload) => apiClient.post("/auth/register", payload);
export const loginUser = (payload) => apiClient.post("/auth/login", payload);
export const fetchCurrentUser = () => apiClient.get("/auth/me");
export const refreshAccessToken = (refreshToken) =>
  apiClient.post(
    "/auth/refresh",
    {},
    {
      headers: {
        Authorization: `Bearer ${refreshToken}`,
      },
    }
  );
