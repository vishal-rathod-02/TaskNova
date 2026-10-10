import apiClient from "../api/client";

export const registerUser = (payload) => apiClient.post("/auth/register", payload);
export const loginUser = (payload) => apiClient.post("/auth/login", payload);
export const fetchCurrentUser = () => apiClient.get("/auth/me");
export const logoutUser = (payload = {}) => apiClient.post("/auth/logout", payload);
export const updateUserPreferences = (payload) => apiClient.patch("/auth/preferences", payload);
export const regenerateCalendarToken = () => apiClient.post("/auth/calendar-token/regenerate");
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

