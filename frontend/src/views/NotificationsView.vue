<script setup>
import { computed, onMounted, ref } from "vue";
import AppIcon from "../components/AppIcon.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import { showToast } from "../composables/toast";
import { useNotificationStore } from "../stores/notifications";

const notificationStore = useNotificationStore();
const error = ref("");
const unreadOnly = ref(false);

const kindLabel = (kind) =>
  ({ deadline_due: "Due soon", overdue: "Overdue", daily_report: "Daily report" }[kind] || kind);

const loadNotifications = async () => {
  error.value = "";
  try {
    await notificationStore.fetchNotifications(unreadOnly.value);
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to load notifications.";
  }
};

const toggleUnread = async () => {
  unreadOnly.value = !unreadOnly.value;
  await loadNotifications();
};

const markRead = async (id) => {
  try {
    await notificationStore.markRead(id);
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to mark notification as read.";
  }
};

const markAllRead = async () => {
  try {
    await notificationStore.markAllRead();
    showToast("Inbox cleared.");
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to clear the inbox.";
  }
};

const formatDate = (date) => new Date(date).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
const isOverdueKind = (kind) => kind === "overdue";
const taskLink = (taskId) => (taskId ? { name: "tasks" } : { name: "dashboard" });

onMounted(loadNotifications);
const items = computed(() => notificationStore.items);
</script>

<template>
  <div class="page-shell">
    <PageHeader title="Notification inbox" description="Deadline reminders and daily productivity reports, newest first.">
      <template #actions>
        <button class="btn-secondary gap-2" type="button" @click="toggleUnread">
          <AppIcon name="inbox" :size="16" />{{ unreadOnly ? "Show all" : "Unread only" }}
        </button>
        <button class="btn-secondary gap-2" type="button" :disabled="!notificationStore.unreadCount" @click="markAllRead">
          <AppIcon name="check" :size="16" />Mark all read
        </button>
      </template>
    </PageHeader>

    <p class="data-label mt-4">{{ notificationStore.unreadCount }} unread</p>
    <p v-if="error" class="field-error mt-4" role="alert">{{ error }}</p>

    <p v-if="notificationStore.loading" class="mt-8 text-sm text-slate dark:text-[#9AA3B2]">Loading notifications...</p>
    <EmptyState
      v-else-if="!items.length"
      class="mt-8"
      title="Inbox is clear"
      description="Deadline reminders from the scheduled job and your daily productivity report will appear here."
    />
    <div v-else class="mt-6 border-t border-slate/20 dark:border-slate/30">
      <article
        v-for="item in items"
        :key="item.id"
        class="ledger-row"
        :class="{ 'opacity-70': item.is_read }"
      >
        <span class="priority-tab" :class="isOverdueKind(item.kind) ? 'priority-overdue' : 'priority-medium'" aria-hidden="true"></span>
        <div class="min-w-0">
          <div class="flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <h3 class="text-base font-medium text-ink dark:text-[#E7E9ED]">{{ item.title }}</h3>
            <span class="data-label">{{ kindLabel(item.kind) }}</span>
          </div>
          <p v-if="item.body" class="mt-1 max-w-[72ch] text-sm leading-5 text-slate dark:text-[#9AA3B2]">{{ item.body }}</p>
          <p class="mt-2 data-label">{{ formatDate(item.created_at) }}</p>
        </div>
        <div class="flex flex-wrap gap-x-3 gap-y-1 sm:justify-end">
          <router-link
            v-if="item.task_id"
            class="min-h-11 px-1 py-3 text-sm font-medium text-ink underline decoration-slate/50 underline-offset-4 hover:decoration-ink dark:text-[#E7E9ED]"
            :to="taskLink(item.task_id)"
          >
            View tasks
          </router-link>
          <button
            v-if="!item.is_read"
            class="min-h-11 px-1 text-sm font-medium text-ink underline decoration-slate/50 underline-offset-4 hover:decoration-ink dark:text-[#E7E9ED]"
            type="button"
            @click="markRead(item.id)"
          >
            Mark read
          </button>
          <span v-else class="status-chip status-done"><span class="status-dot"></span>Read</span>
        </div>
      </article>
    </div>
  </div>
</template>
