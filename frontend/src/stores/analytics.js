import { defineStore } from "pinia";
import { getAdminDashboard, getPersonalDashboard } from "../services/analytics";

export const useAnalyticsStore = defineStore("analytics", {
  state: () => ({
    stats: null,
    source: "database",
    loading: false,
  }),
  actions: {
    async fetchStats(isAdmin = false) {
      this.loading = true;
      try {
        const { data } = await (isAdmin ? getAdminDashboard() : getPersonalDashboard());
        this.stats = data.stats;
        this.source = data.source || "database";
      } finally {
        this.loading = false;
      }
    },
  },
});
