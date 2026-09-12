import apiClient from "../api/client";

export const getPersonalDashboard = () => apiClient.get("/analytics/me");
export const getAdminDashboard = () => apiClient.get("/analytics/admin");
