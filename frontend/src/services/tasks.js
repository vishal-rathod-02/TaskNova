import apiClient from "../api/client";

export const listTasks = (params) => apiClient.get("/tasks", { params });
export const getTask = (id) => apiClient.get(`/tasks/${id}`);
export const createTask = (payload) => apiClient.post("/tasks", payload);
export const updateTask = (id, payload) => apiClient.put(`/tasks/${id}`, payload);
export const completeTask = (id) => apiClient.post(`/tasks/${id}/complete`);
export const deleteTask = (id) => apiClient.delete(`/tasks/${id}`);
export const getTaskActivity = (id) => apiClient.get(`/tasks/${id}/activity`);
