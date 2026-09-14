import apiClient from "../api/client";

export const getPersonalDashboard = () => apiClient.get("/analytics/me");
export const getAdminDashboard = () => apiClient.get("/analytics/admin");
export const getLatestReport = () => apiClient.get("/analytics/report/latest");
export const getReportDigest = (date) => apiClient.get("/analytics/report/digest", { params: date ? { date } : {} });
export const getReportHistory = (days = 7) => apiClient.get("/analytics/report/history", { params: { days } });

