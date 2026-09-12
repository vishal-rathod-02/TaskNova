import { defineStore } from "pinia";
import {
  completeTask as completeTaskRequest,
  createTask as createTaskRequest,
  deleteTask as deleteTaskRequest,
  listTasks,
  updateTask as updateTaskRequest,
} from "../services/tasks";

export const useTaskStore = defineStore("tasks", {
  state: () => ({
    items: [],
    loading: false,
    pagination: { page: 1, per_page: 50, total: 0, pages: 1 },
  }),
  getters: {
    todoTasks: (state) => state.items.filter((task) => task.status === "todo"),
    inProgressTasks: (state) => state.items.filter((task) => task.status === "in_progress"),
    doneTasks: (state) => state.items.filter((task) => task.status === "done"),
  },
  actions: {
    async fetchTasks(filters = {}) {
      this.loading = true;
      try {
        const params = Object.fromEntries(Object.entries(filters).filter(([, value]) => value !== "" && value !== null && value !== undefined));
        const { data } = await listTasks(params);
        this.items = data.tasks;
        if (data.pagination) {
          this.pagination = data.pagination;
        }
      } finally {
        this.loading = false;
      }
    },
    async createTask(payload) {
      const { data } = await createTaskRequest(payload);
      this.items.unshift(data.task);
    },
    async completeTask(id) {
      const { data } = await completeTaskRequest(id);
      this.items = this.items.map((task) => (task.id === id ? data.task : task));
    },
    async updateTask(id, payload) {
      const { data } = await updateTaskRequest(id, payload);
      this.items = this.items.map((task) => (task.id === id ? data.task : task));
    },
    async deleteTask(id) {
      await deleteTaskRequest(id);
      this.items = this.items.filter((task) => task.id !== id);
    },
  },
});
