import { defineStore } from "pinia";
import apiClient from "../api/client";

export const useTaskStore = defineStore("tasks", {
  state: () => ({
    items: [],
    loading: false,
  }),
  getters: {
    todoTasks: (state) => state.items.filter((task) => task.status === "todo"),
    inProgressTasks: (state) => state.items.filter((task) => task.status === "in_progress"),
    doneTasks: (state) => state.items.filter((task) => task.status === "done"),
  },
  actions: {
    async fetchTasks(projectId = null) {
      this.loading = true;
      try {
        const params = projectId ? { project_id: projectId } : {};
        const { data } = await apiClient.get("/tasks", { params });
        this.items = data.tasks;
      } finally {
        this.loading = false;
      }
    },
    async createTask(payload) {
      const { data } = await apiClient.post("/tasks", payload);
      this.items.unshift(data.task);
    },
    async completeTask(id) {
      const { data } = await apiClient.post(`/tasks/${id}/complete`);
      this.items = this.items.map((task) => (task.id === id ? data.task : task));
    },
    async updateTask(id, payload) {
      const { data } = await apiClient.put(`/tasks/${id}`, payload);
      this.items = this.items.map((task) => (task.id === id ? data.task : task));
    },
    async deleteTask(id) {
      await apiClient.delete(`/tasks/${id}`);
      this.items = this.items.filter((task) => task.id !== id);
    },
  },
});
