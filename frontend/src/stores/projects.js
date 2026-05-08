import { defineStore } from "pinia";
import apiClient from "../api/client";

export const useProjectStore = defineStore("projects", {
  state: () => ({
    items: [],
    loading: false,
  }),
  actions: {
    async fetchProjects() {
      this.loading = true;
      try {
        const { data } = await apiClient.get("/projects");
        this.items = data.projects;
      } finally {
        this.loading = false;
      }
    },
    async createProject(payload) {
      const { data } = await apiClient.post("/projects", payload);
      this.items.unshift(data.project);
    },
    async deleteProject(id) {
      await apiClient.delete(`/projects/${id}`);
      this.items = this.items.filter((project) => project.id !== id);
    },
  },
});
