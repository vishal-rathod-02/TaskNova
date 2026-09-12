import { defineStore } from "pinia";
import {
  createProject as createProjectRequest,
  deleteProject as deleteProjectRequest,
  listProjects,
  updateProject as updateProjectRequest,
} from "../services/projects";

export const useProjectStore = defineStore("projects", {
  state: () => ({
    items: [],
    loading: false,
  }),
  actions: {
    async fetchProjects() {
      this.loading = true;
      try {
        const { data } = await listProjects();
        this.items = data.projects;
      } finally {
        this.loading = false;
      }
    },
    async createProject(payload) {
      const { data } = await createProjectRequest(payload);
      this.items.unshift(data.project);
    },
    async updateProject(id, payload) {
      const { data } = await updateProjectRequest(id, payload);
      this.items = this.items.map((project) => (project.id === id ? data.project : project));
    },
    async deleteProject(id) {
      await deleteProjectRequest(id);
      this.items = this.items.filter((project) => project.id !== id);
    },
  },
});
