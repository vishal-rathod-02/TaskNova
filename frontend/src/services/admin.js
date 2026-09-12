import apiClient from "../api/client";

export const listUsers = () => apiClient.get("/admin/users");
export const updateUserBlock = (id, isBlocked) => apiClient.patch(`/admin/users/${id}/block`, { is_blocked: isBlocked });
export const deleteUser = (id) => apiClient.delete(`/admin/users/${id}`);
