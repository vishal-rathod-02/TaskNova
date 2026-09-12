import { defineStore } from "pinia";
import {
  getLatestReport,
  listNotifications,
  markAllNotificationsRead as markAllNotificationsReadRequest,
  markNotificationRead as markNotificationReadRequest,
} from "../services/notifications";

export const useNotificationStore = defineStore("notifications", {
  state: () => ({
    items: [],
    unreadCount: 0,
    latestReport: null,
    loading: false,
  }),
  actions: {
    async fetchNotifications(unreadOnly = false) {
      this.loading = true;
      try {
        const { data } = await listNotifications(unreadOnly ? { unread_only: true } : {});
        this.items = data.notifications;
        this.unreadCount = data.unread_count;
      } finally {
        this.loading = false;
      }
    },
    async fetchLatestReport() {
      const { data } = await getLatestReport();
      this.latestReport = data.report;
    },
    async markRead(id) {
      const { data } = await markNotificationReadRequest(id);
      this.items = this.items.map((item) => (item.id === id ? data.notification : item));
      this.unreadCount = Math.max(this.unreadCount - 1, 0);
    },
    async markAllRead() {
      await markAllNotificationsReadRequest();
      this.items = this.items.map((item) => ({ ...item, is_read: true }));
      this.unreadCount = 0;
    },
  },
});
