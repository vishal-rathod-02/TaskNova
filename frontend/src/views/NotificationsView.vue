<script setup>
import { computed, onMounted, ref } from "vue";
import AppIcon from "../components/AppIcon.vue";
import AppLoader from "../components/AppLoader.vue";
import ConfirmModal from "../components/ConfirmModal.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import SkeletonLoader from "../components/SkeletonLoader.vue";
import TaskDetailModal from "../components/TaskDetailModal.vue";
import { showToast } from "../composables/toast";
import { useNotificationStore } from "../stores/notifications";
import { withMinLoading } from "../utils/async";

const notificationStore = useNotificationStore();
const error = ref("");
const selectedFilter = ref("all"); // 'all' | 'unread' | 'deadlines' | 'reports'

const isMarkAllModalOpen = ref(false);
const markAllLoading = ref(false);

const isTaskDetailOpen = ref(false);
const selectedTaskId = ref(null);

const loadNotifications = async () => {
  error.value = "";
  try {
    await withMinLoading(
      notificationStore.fetchNotifications(selectedFilter.value === "unread"),
      1800
    );
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to load notifications.";
  }
};

const openTaskDetails = (taskId) => {
  selectedTaskId.value = taskId;
  isTaskDetailOpen.value = true;
};

const kindLabel = (kind) =>
  ({ deadline_due: "Due Soon", overdue: "Overdue Deadline", daily_report: "Daily Productivity Report" }[kind] || kind);

const kindIcon = (kind) => {
  switch (kind) {
    case "overdue":
      return "alert";
    case "deadline_due":
      return "clock";
    case "daily_report":
      return "sparkles";
    default:
      return "bell";
  }
};

const kindStyles = (kind) => {
  switch (kind) {
    case "overdue":
      return "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-900/40";
    case "deadline_due":
      return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-900/40";
    case "daily_report":
      return "bg-brand-50 text-brand-700 border-brand-200 dark:bg-brand-950/50 dark:text-brand-300 dark:border-brand-900/40";
    default:
      return "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300";
  }
};

const filterNotifications = (filterId) => {
  selectedFilter.value = filterId;
  loadNotifications();
};

const markRead = async (id) => {
  try {
    await notificationStore.markRead(id);
    showToast("Notification marked as read.");
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to mark notification as read.";
  }
};

const confirmMarkAll = async () => {
  markAllLoading.value = true;
  try {
    await notificationStore.markAllRead();
    showToast("All notifications marked as read.");
    isMarkAllModalOpen.value = false;
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to clear the inbox.";
  } finally {
    markAllLoading.value = false;
  }
};

const formatRelativeTime = (isoDate) => {
  if (!isoDate) return "";
  const date = new Date(isoDate);
  const now = new Date();
  const diffSec = Math.floor((now - date) / 1000);
  if (diffSec < 60) return "Just now";
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
};

const displayedNotifications = computed(() => {
  const items = notificationStore.items;
  if (selectedFilter.value === "deadlines") {
    return items.filter((i) => i.kind === "deadline_due" || i.kind === "overdue");
  }
  if (selectedFilter.value === "reports") {
    return items.filter((i) => i.kind === "daily_report");
  }
  return items;
});

onMounted(loadNotifications);
</script>

<template>
  <div class="page-shell">
    <PageHeader
      title="Notification Inbox"
      description="Automated assignment deadline warnings, daily productivity digests, and system updates."
      :badge="`${notificationStore.unreadCount} Unread`"
    >
      <template #actions>
        <button
          class="btn-secondary gap-2"
          type="button"
          :disabled="!notificationStore.unreadCount"
          @click="isMarkAllModalOpen = true"
        >
          <AppIcon name="check-circle" :size="16" /> Mark All Read
        </button>
      </template>
    </PageHeader>

    <!-- Filter Pills Bar -->
    <div class="mt-8 flex flex-wrap items-center gap-2 border-b border-slate-200/80 pb-4 dark:border-slate-800">
      <button
        type="button"
        class="rounded-xl px-3.5 py-1.5 text-xs font-bold transition-all"
        :class="selectedFilter === 'all' ? 'bg-brand-600 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-100 dark:bg-night-card dark:text-slate-300 dark:hover:bg-slate-800'"
        @click="filterNotifications('all')"
      >
        All Updates
      </button>

      <button
        type="button"
        class="rounded-xl px-3.5 py-1.5 text-xs font-bold transition-all"
        :class="selectedFilter === 'unread' ? 'bg-brand-600 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-100 dark:bg-night-card dark:text-slate-300 dark:hover:bg-slate-800'"
        @click="filterNotifications('unread')"
      >
        Unread Only ({{ notificationStore.unreadCount }})
      </button>

      <button
        type="button"
        class="rounded-xl px-3.5 py-1.5 text-xs font-bold transition-all"
        :class="selectedFilter === 'deadlines' ? 'bg-brand-600 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-100 dark:bg-night-card dark:text-slate-300 dark:hover:bg-slate-800'"
        @click="filterNotifications('deadlines')"
      >
        Deadline Warnings
      </button>

      <button
        type="button"
        class="rounded-xl px-3.5 py-1.5 text-xs font-bold transition-all"
        :class="selectedFilter === 'reports' ? 'bg-brand-600 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-100 dark:bg-night-card dark:text-slate-300 dark:hover:bg-slate-800'"
        @click="filterNotifications('reports')"
      >
        Daily Digests
      </button>

      <button
        class="btn-ghost ml-auto text-xs"
        type="button"
        :disabled="notificationStore.loading"
        @click="loadNotifications"
      >
        <AppIcon name="refresh" :size="14" :class="{ 'animate-spin': notificationStore.loading }" /> Refresh
      </button>
    </div>

    <!-- Error Alert -->
    <p v-if="error" class="field-error mt-4" role="alert">
      <AppIcon name="alert" :size="16" /> {{ error }}
    </p>

    <!-- Loading State with UIverse Skeleton & AppLoader -->
    <div v-if="notificationStore.loading" class="mt-6 space-y-4">
      <SkeletonLoader type="rows" :count="4" />
      <AppLoader size="sm" text="Fetching notification inbox updates" />
    </div>

    <!-- Empty State -->
    <EmptyState
      v-else-if="!displayedNotifications.length"
      class="mt-8"
      icon="check-circle"
      title="Inbox is completely clear"
      description="You have caught up with all assignment deadline alerts and productivity summaries."
    />

    <!-- Notification Feed -->
    <div v-else class="mt-6 space-y-3">
      <article
        v-for="item in displayedNotifications"
        :key="item.id"
        class="surface-card flex flex-col justify-between gap-3 p-4 transition-all duration-200 sm:flex-row sm:items-center"
        :class="{ 'opacity-70 bg-slate-50/50 dark:bg-night-card/40': item.is_read }"
      >
        <!-- Notification Info -->
        <div class="flex items-start gap-3.5">
          <div
            class="flex h-10 w-10 flex-none items-center justify-center rounded-xl border"
            :class="kindStyles(item.kind)"
          >
            <AppIcon :name="kindIcon(item.kind)" :size="18" />
          </div>

          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <h3 class="font-sans text-sm font-bold text-slate-900 dark:text-white">
                {{ item.title }}
              </h3>
              <span class="rounded-md border px-2 py-0.5 font-mono text-[10px] font-bold" :class="kindStyles(item.kind)">
                {{ kindLabel(item.kind) }}
              </span>
              <span class="font-mono text-xs text-slate-400">
                · {{ formatRelativeTime(item.created_at) }}
              </span>
            </div>

            <p v-if="item.body" class="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
              {{ item.body }}
            </p>
          </div>
        </div>

        <!-- Notification Actions -->
        <div class="flex items-center gap-2 self-end border-t border-slate-100 pt-2 sm:self-center sm:border-t-0 sm:pt-0">
          <button
            v-if="item.task_id"
            type="button"
            class="btn-secondary text-xs gap-1.5"
            @click="openTaskDetails(item.task_id)"
          >
            <AppIcon name="tasks" :size="14" /> View Task Details &rarr;
          </button>

          <button
            v-if="!item.is_read"
            type="button"
            class="rounded-xl border border-brand-200 bg-brand-50 px-3 py-1.5 text-xs font-bold text-brand-700 hover:bg-brand-100 dark:border-brand-900/50 dark:bg-brand-950/60 dark:text-brand-300"
            @click="markRead(item.id)"
          >
            Mark Read
          </button>
          <span v-else class="status-chip status-done text-xs">
            <span class="status-dot"></span> Read
          </span>
        </div>
      </article>
    </div>

    <!-- Modal for Task Details opened from notification -->
    <TaskDetailModal
      :is-open="isTaskDetailOpen"
      :task-id="selectedTaskId"
      @close="isTaskDetailOpen = false"
      @updated="loadNotifications"
    />

    <!-- Confirm Modal for Mark All Read -->
    <ConfirmModal
      :is-open="isMarkAllModalOpen"
      title="Mark All Notifications as Read?"
      message="This will clear all pending unread indicators in your workspace inbox."
      confirm-text="Mark All Read"
      :is-danger="false"
      :loading="markAllLoading"
      @cancel="isMarkAllModalOpen = false"
      @confirm="confirmMarkAll"
    />
  </div>
</template>
