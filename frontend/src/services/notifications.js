import apiClient from "../api/client";

export const listNotifications = (params) => apiClient.get("/notifications", { params });
export const markNotificationRead = (id) => apiClient.post(`/notifications/${id}/read`);
export const markAllNotificationsRead = () => apiClient.post("/notifications/read-all");
export const getLatestReport = () => apiClient.get("/analytics/report/latest");
export const getReportHistory = (days = 7) => apiClient.get("/analytics/report/history", { params: { days } });
