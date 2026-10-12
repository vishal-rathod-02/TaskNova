import apiClient from "../api/client";

export const listUsers = () => apiClient.get("/admin/users");
export const updateUserBlock = (id, isBlocked) => apiClient.patch(`/admin/users/${id}/block`, { is_blocked: isBlocked });
export const deleteUser = (id) => apiClient.delete(`/admin/users/${id}`);
export const listRoutineTemplates = () => apiClient.get("/admin/timetable/templates");
export const updateRoutineTemplate = (name, isEnabled) =>
  apiClient.patch(`/admin/timetable/templates/${name}`, { is_enabled: isEnabled });
