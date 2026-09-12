import apiClient from "../api/client";

export const listProjects = () => apiClient.get("/projects");
export const getProject = (id) => apiClient.get(`/projects/${id}`);
export const createProject = (payload) => apiClient.post("/projects", payload);
export const updateProject = (id, payload) => apiClient.put(`/projects/${id}`, payload);
export const deleteProject = (id) => apiClient.delete(`/projects/${id}`);
export const listProjectTasks = (projectId, params) => apiClient.get(`/projects/${projectId}/tasks`, { params });
export const createProjectTask = (projectId, payload) => apiClient.post(`/projects/${projectId}/tasks`, payload);
