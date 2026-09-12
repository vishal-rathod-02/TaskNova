import { defineStore } from "pinia";
import { deleteUser as deleteUserRequest, listUsers, updateUserBlock as updateUserBlockRequest } from "../services/admin";

export const useAdminStore = defineStore("admin", {
  state: () => ({
    users: [],
    loading: false,
    error: "",
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
  },
});
