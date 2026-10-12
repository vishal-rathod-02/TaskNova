import { defineStore } from "pinia";
import {
  deleteUser as deleteUserRequest,
  listRoutineTemplates,
  listUsers,
  updateRoutineTemplate as updateRoutineTemplateRequest,
  updateUserBlock as updateUserBlockRequest,
} from "../services/admin";

export const useAdminStore = defineStore("admin", {
  state: () => ({
    users: [],
    loading: false,
    error: "",
    templates: [],
    templatesLoading: false,
  }),
  actions: {
    async fetchUsers() {
      this.loading = true;
      this.error = "";
      try {
        const { data } = await listUsers();
        this.users = data.users;
      } catch (requestError) {
        this.error = requestError.response?.data?.message || "Unable to load user accounts.";
        throw requestError;
      } finally {
        this.loading = false;
      }
    },
    async toggleBlock(user) {
      const { data } = await updateUserBlockRequest(user.id, !user.is_blocked);
      this.users = this.users.map((item) => (item.id === user.id ? data.user : item));
      return data.user;
    },
    async removeUser(id) {
      await deleteUserRequest(id);
      this.users = this.users.filter((item) => item.id !== id);
    },
    async fetchRoutineTemplates() {
      this.templatesLoading = true;
      try {
        const { data } = await listRoutineTemplates();
        this.templates = data.templates;
      } finally {
        this.templatesLoading = false;
      }
    },
    async toggleRoutineTemplate(template) {
      const { data } = await updateRoutineTemplateRequest(template.name, !template.is_enabled);
      const updated = { ...template, ...data.template };
      this.templates = this.templates.map((item) => (item.name === updated.name ? updated : item));
      return updated;
    },
  },
});
