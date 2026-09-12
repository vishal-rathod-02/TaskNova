import { defineStore } from "pinia";
import { fetchCurrentUser, loginUser, refreshAccessToken, registerUser } from "../services/auth";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    accessToken: localStorage.getItem("access_token") || "",
    refreshToken: localStorage.getItem("refresh_token") || "",
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isAdmin: (state) => state.user?.role === "admin",
  },
  actions: {
    async register(payload) {
      await registerUser(payload);
    },
    async login(payload) {
      const { data } = await loginUser(payload);
      this.accessToken = data.access_token;
      this.refreshToken = data.refresh_token;
      this.user = data.user;
      localStorage.setItem("access_token", this.accessToken);
      localStorage.setItem("refresh_token", this.refreshToken);
    },
    async fetchCurrentUser() {
      if (!this.accessToken) return;
      const { data } = await fetchCurrentUser();
      this.user = data.user;
    },
    async refreshAccessToken() {
      if (!this.refreshToken) throw new Error("No refresh token");
      const { data } = await refreshAccessToken(this.refreshToken);
      this.accessToken = data.access_token;
      localStorage.setItem("access_token", this.accessToken);
    },
    logout() {
      this.user = null;
      this.accessToken = "";
      this.refreshToken = "";
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    },
  },
});
