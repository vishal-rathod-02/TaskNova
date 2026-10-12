import apiClient from "../api/client";

export const listSlots = (params) => apiClient.get("/timetable", { params });
export const createSlot = (payload) => apiClient.post("/timetable", payload);
export const updateSlot = (id, payload) => apiClient.put(`/timetable/${id}`, payload);
export const deleteSlot = (id) => apiClient.delete(`/timetable/${id}`);
export const autoSchedule = (payload) => apiClient.post("/timetable/auto-schedule", payload);
export const applyTemplate = (payload) => apiClient.post("/timetable/apply-template", payload);
export const listAvailableTemplates = () => apiClient.get("/timetable/templates");
