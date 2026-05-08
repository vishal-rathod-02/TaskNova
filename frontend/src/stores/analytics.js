import { defineStore } from "pinia";
import apiClient from "../api/client";

export const useAnalyticsStore = defineStore("analytics", {
  state: () => ({
    stats: null,
    statusBreakdown: [],
  }),
  actions: {
    async fetchStats() {
      const [{ data: statsData }, { data: breakdownData }] = await Promise.all([
        apiClient.get("/analytics/dashboard"),
        apiClient.get("/analytics/status-breakdown"),
      ]);
      this.stats = statsData.stats;
      this.statusBreakdown = breakdownData.items;
    },
  },
});
