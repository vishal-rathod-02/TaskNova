<script setup>
import { computed, onMounted, ref } from "vue";
import AnimatedBarChart from "../components/AnimatedBarChart.vue";
import AnimatedNumber from "../components/AnimatedNumber.vue";
import AppIcon from "../components/AppIcon.vue";
import AppLoader from "../components/AppLoader.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import SkeletonLoader from "../components/SkeletonLoader.vue";
import StudyHeatmap from "../components/StudyHeatmap.vue";
import TaskModal from "../components/TaskModal.vue";
import { showToast } from "../composables/toast";
import { useAdminStore } from "../stores/admin";
import { useAnalyticsStore } from "../stores/analytics";
import { useAuthStore } from "../stores/auth";
import { useNotificationStore } from "../stores/notifications";
import { useProjectStore } from "../stores/projects";
import { useTaskStore } from "../stores/tasks";
import { withMinLoading } from "../utils/async";

const adminStore = useAdminStore();
const analyticsStore = useAnalyticsStore();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const projectStore = useProjectStore();
const taskStore = useTaskStore();

const error = ref("");
const isCreateTaskOpen = ref(false);
const creatingTaskLoading = ref(false);
const taskFormErrors = ref({});

const stats = computed(() => analyticsStore.stats || {});
const isEmpty = computed(() => !analyticsStore.loading && !authStore.isAdmin && stats.value.total_tasks === 0);
const report = computed(() => notificationStore.latestReport);
const latestUsers = computed(() => [...(adminStore.users || [])].sort((a, b) => b.id - a.id).slice(0, 4));
const adminCompletionRate = computed(() => {
  const total = stats.value.total_tasks || 0;
  if (!total) return 0;
  return Math.round(((stats.value.completed_tasks || 0) / total) * 100);
});

const greeting = computed(() => {
  const hour = new Date().getHours();
  const name = authStore.user?.full_name?.split(" ")[0] || "Student";
  if (hour < 12) return `Good morning, ${name} 🎓`;
  if (hour < 18) return `Good afternoon, ${name} 🎓`;
  return `Good evening, ${name} 🎓`;
});

const loadDashboard = async () => {
  error.value = "";
  try {
      await withMinLoading(
        Promise.all([
          analyticsStore.fetchStats(authStore.isAdmin),
          authStore.isAdmin ? adminStore.fetchUsers().catch(() => {}) : Promise.resolve(),
          authStore.isAdmin ? Promise.resolve() : notificationStore.fetchNotifications(),
        authStore.isAdmin ? Promise.resolve() : notificationStore.fetchLatestReport().catch(() => {}),
        projectStore.fetchProjects().catch(() => {}),
        authStore.isAdmin ? Promise.resolve() : taskStore.fetchTasks().catch(() => {}),
      ]),
      1800
    );
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to load dashboard data.";
  }
};

const handleCreateTask = async (formData) => {
  creatingTaskLoading.value = true;
  taskFormErrors.value = {};
  try {
    const toUtcIso = (localInput) => (localInput ? new Date(localInput).toISOString() : null);
    await taskStore.createTask({
      ...formData,
      project_id: Number(formData.project_id),
      due_date: toUtcIso(formData.due_date),
    });
    isCreateTaskOpen.value = false;
    showToast("Task added to your academic ledger.");
    await loadDashboard();
  } catch (err) {
    taskFormErrors.value = err.response?.data?.errors || {};
    error.value = err.response?.data?.message || "Unable to create task.";
  } finally {
    creatingTaskLoading.value = false;
  }
};

onMounted(loadDashboard);
</script>

<template>
  <div class="page-shell">
    <!-- Header -->
    <PageHeader
      :title="authStore.isAdmin ? 'System Governance Overview' : greeting"
      :description="authStore.isAdmin ? 'A high-level read on user accounts, system courses, and task health.' : 'Track your academic milestones, upcoming deadlines, and study momentum.'"
      :badge="authStore.isAdmin ? 'Admin Console' : 'Active Semester'"
    >
      <template #actions>
        <button
          v-if="!authStore.isAdmin"
          class="btn-primary gap-2"
          type="button"
          @click="isCreateTaskOpen = true"
        >
          <AppIcon name="plus" :size="16" /> Quick Task
        </button>
        <button
          class="btn-secondary gap-2"
          type="button"
          :disabled="analyticsStore.loading"
          @click="loadDashboard"
        >
          <AppIcon name="refresh" :size="16" :class="{ 'animate-spin': analyticsStore.loading }" />
          {{ analyticsStore.loading ? "Updating..." : "Refresh" }}
        </button>
      </template>
    </PageHeader>

    <!-- Data source tag -->
    <div class="mt-3 flex items-center gap-2">
      <span class="inline-flex items-center gap-1.5 font-mono text-xs text-slate-400">
        <span
          class="h-2 w-2 rounded-full"
          :class="analyticsStore.source === 'cache' ? 'bg-amber-400' : 'bg-emerald-400'"
        ></span>
        Synced from {{ analyticsStore.source === 'cache' ? 'Cache snapshot' : 'live database' }}
      </span>
    </div>

    <!-- Urgent Notification Callout Banner -->
    <section
      v-if="!authStore.isAdmin && notificationStore.unreadCount"
      class="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-rose-200 bg-gradient-to-r from-rose-50/90 to-amber-50/50 p-4 dark:border-rose-900/40 dark:from-rose-950/40 dark:to-amber-950/20 shadow-sm transition-all duration-300 hover:shadow-md"
      aria-live="polite"
    >
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 flex-none items-center justify-center rounded-xl bg-rose-100 text-rose-600 dark:bg-rose-900/60 dark:text-rose-300">
          <AppIcon name="alert" :size="20" class="animate-pulse" />
        </div>
        <div>
          <h4 class="font-display text-sm font-bold text-slate-900 dark:text-white">
            {{ notificationStore.unreadCount }} Pending Deadline Reminder{{ notificationStore.unreadCount === 1 ? "" : "s" }}
          </h4>
          <p class="text-xs text-slate-600 dark:text-slate-400">
            You have upcoming assignments or tasks that need attention.
          </p>
        </div>
      </div>
      <router-link
        to="/notifications"
        class="btn-secondary text-xs"
      >
        View Inbox &rarr;
      </router-link>
    </section>

    <!-- Error notice -->
    <p v-if="error" class="field-error mt-4" aria-live="polite">
      <AppIcon name="alert" :size="16" /> {{ error }}
    </p>

    <!-- Loading State with UIverse Skeleton & Orbital AppLoader -->
    <div v-if="analyticsStore.loading && !analyticsStore.stats" class="mt-8 space-y-6">
      <SkeletonLoader type="metrics" :count="4" />
      <AppLoader size="md" text="Synchronizing academic workplace metrics" />
    </div>

    <!-- Admin Overview Cards with Animated Numbers -->
    <section v-else-if="authStore.isAdmin" class="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <div class="metric-card border-l-4 border-l-brand-500 transition-all duration-300 hover:-translate-y-1">
        <span class="data-label">Active Users</span>
        <p class="metric-value mt-2">
          <AnimatedNumber :value="stats.active_users || 0" />
        </p>
        <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">of {{ stats.total_users || 0 }} total registered</p>
      </div>

      <div class="metric-card border-l-4 border-l-academic-purple transition-all duration-300 hover:-translate-y-1">
        <span class="data-label">Courses & Projects</span>
        <p class="metric-value mt-2">
          <AnimatedNumber :value="stats.total_projects || 0" />
        </p>
        <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">Active workspaces</p>
      </div>

      <div class="metric-card border-l-4 border-l-rose-500 transition-all duration-300 hover:-translate-y-1">
        <span class="data-label">System Overdue Tasks</span>
        <p class="metric-value mt-2 text-rose-600 dark:text-rose-400">
          <AnimatedNumber :value="stats.overdue_tasks || 0" />
        </p>
        <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">Need immediate follow-up</p>
      </div>

      <div class="metric-card border-l-4 border-l-emerald-500 transition-all duration-300 hover:-translate-y-1">
        <span class="data-label">Activity (Last 24h)</span>
        <p class="metric-value mt-2 text-emerald-600 dark:text-emerald-400">
          <AnimatedNumber :value="stats.activity_last_24h || 0" />
        </p>
        <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">Recorded audit events</p>
      </div>
    </section>

    <!-- Admin action row: governance links + workspace completion -->
    <section v-if="authStore.isAdmin && analyticsStore.stats" class="mt-6 grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(300px,0.7fr)]">
      <!-- Governance shortcuts -->
      <div class="surface-card">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
          <h2 class="section-title">Governance Actions</h2>
          <AppIcon name="admin" :size="18" class="text-slate-400" />
        </div>
        <div class="mt-4 grid gap-2.5 sm:grid-cols-3">
          <router-link to="/admin" class="btn-secondary min-h-11 justify-center gap-1.5 text-xs">
            <AppIcon name="users" :size="15" class="flex-none" /> User Directory
          </router-link>
          <router-link to="/tasks" class="btn-secondary min-h-11 justify-center gap-1.5 text-xs">
            <AppIcon name="tasks" :size="15" class="flex-none" /> Task Ledger
          </router-link>
          <router-link to="/notifications" class="btn-secondary min-h-11 justify-center gap-1.5 text-xs">
            <AppIcon name="bell" :size="15" class="flex-none" /> Inbox
            <span v-if="stats.overdue_tasks > 0" class="flex h-5 min-w-5 flex-none items-center justify-center rounded-full bg-rose-500 px-1.5 font-mono text-[10px] font-extrabold text-white">{{ stats.overdue_tasks }}</span>
          </router-link>
        </div>
        <div class="mt-4">
          <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Workspace completion</span>
            <span class="font-mono font-bold text-slate-700 dark:text-slate-200">{{ adminCompletionRate }}%</span>
          </div>
          <div class="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full bg-gradient-to-r from-brand-500 to-emerald-500 transition-all duration-700" :style="{ width: `${adminCompletionRate}%` }"></div>
          </div>
          <p class="mt-2 font-mono text-[11px] text-slate-500 dark:text-slate-400">
            {{ stats.blocked_users || 0 }} blocked · {{ stats.total_projects || 0 }} projects · {{ stats.completed_tasks || 0 }}/{{ stats.total_tasks || 0 }} tasks done
          </p>
        </div>
      </div>

      <!-- Latest registered users -->
      <div class="surface-card">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
          <h2 class="section-title">Latest Signups</h2>
          <router-link to="/admin" class="text-xs font-semibold text-brand-600 hover:underline dark:text-brand-400">Directory &rarr;</router-link>
        </div>
        <div v-if="!latestUsers.length" class="py-6 text-center text-xs text-slate-400">No accounts yet.</div>
        <div v-else class="mt-3 space-y-2">
          <div v-for="u in latestUsers" :key="u.id" class="flex min-w-0 items-center gap-2.5 rounded-xl bg-slate-50 p-2.5 dark:bg-night-surface">
            <span class="flex h-8 w-8 flex-none items-center justify-center rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-500 font-display text-xs font-bold text-white">{{ (u.full_name || "U").charAt(0).toUpperCase() }}</span>
            <span class="min-w-0 flex-1">
              <span class="block truncate text-xs font-bold text-slate-900 dark:text-white">{{ u.full_name }}</span>
              <span class="block truncate font-mono text-[11px] text-slate-500 dark:text-slate-400">{{ u.email }}</span>
            </span>
            <span v-if="u.is_blocked" class="flex-none rounded-md bg-rose-50 px-2 py-0.5 text-[10px] font-bold text-rose-600 dark:bg-rose-950/50 dark:text-rose-400">Blocked</span>
            <span v-else class="flex-none rounded-md bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400">{{ u.role }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Empty State for new users -->
    <EmptyState
      v-else-if="isEmpty"
      class="mt-10"
      title="Your Academic Workspace is Ready"
      description="Create your first Course or Project to start organizing assignments, study schedules, and task milestones."
    >
      <template #actions>
        <router-link class="btn-primary gap-2" to="/projects">
          <AppIcon name="plus" :size="16" /> Create Your First Course
        </router-link>
      </template>
    </EmptyState>

    <!-- Student Dashboard Main Grid -->
    <template v-else-if="!authStore.isAdmin">
      <!-- Daily Report Summary Banner -->
      <section
        v-if="report"
        class="surface mt-6 flex flex-wrap items-center justify-between gap-4 p-5"
      >
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300">
            <AppIcon name="sparkles" :size="20" />
          </div>
          <div>
            <span class="data-label">Daily Productivity Digest · {{ report.report_date }}</span>
            <p class="mt-0.5 text-sm font-semibold text-slate-900 dark:text-white">
              {{ report.completed_tasks }} of {{ report.total_tasks }} items completed · {{ report.overdue_tasks }} overdue
            </p>
          </div>
        </div>
        <router-link
          to="/notifications"
          class="text-xs font-semibold text-brand-600 hover:underline dark:text-brand-400"
        >
          View Full Breakdown &rarr;
        </router-link>
      </section>

      <!-- KPI Metrics Grid with Animated Numbers -->
      <section class="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <!-- Open Tasks -->
        <div class="metric-card border-l-4 border-l-brand-500 transition-all duration-300 hover:-translate-y-1">
          <span class="data-label">Open Tasks</span>
          <p class="metric-value mt-2">
            <AnimatedNumber :value="(stats.total_tasks || 0) - (stats.completed_tasks || 0)" />
          </p>
          <div class="mt-3 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>In progress or to do</span>
            <router-link to="/tasks" class="font-semibold text-brand-600 hover:underline dark:text-brand-400">View tasks</router-link>
          </div>
        </div>

        <!-- Completed Tasks -->
        <div class="metric-card border-l-4 border-l-emerald-500 transition-all duration-300 hover:-translate-y-1">
          <span class="data-label">Completed Tasks</span>
          <p class="metric-value mt-2 text-emerald-600 dark:text-emerald-400">
            <AnimatedNumber :value="stats.completed_tasks || 0" />
          </p>
          <div class="mt-3 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Logged as done</span>
            <span class="font-semibold text-emerald-600">Great progress!</span>
          </div>
        </div>

        <!-- Overdue Tasks -->
        <div class="metric-card border-l-4 border-l-rose-500 transition-all duration-300 hover:-translate-y-1">
          <span class="data-label">Overdue Deadlines</span>
          <p class="metric-value mt-2 text-rose-600 dark:text-rose-400">
            <AnimatedNumber :value="stats.overdue_tasks || 0" />
          </p>
          <div class="mt-3 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Passed scheduled due date</span>
            <span v-if="stats.overdue_tasks > 0" class="font-semibold text-rose-600">Needs attention</span>
            <span v-else class="font-semibold text-emerald-600">All caught up</span>
          </div>
        </div>

        <!-- Completion Rate Progress -->
        <div class="metric-card border-l-4 border-l-indigo-500 transition-all duration-300 hover:-translate-y-1">
          <span class="data-label">Completion Velocity</span>
          <p class="metric-value mt-2">
            <AnimatedNumber :value="stats.completion_rate || 0" suffix="%" />
          </p>
          <div class="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <div
              class="h-full rounded-full bg-gradient-to-r from-brand-500 to-emerald-500 transition-all duration-700 ease-out"
              :style="{ width: `${stats.completion_rate || 0}%` }"
            ></div>
          </div>
        </div>
      </section>

      <!-- Analytics & Performance Section -->
      <section class="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1.3fr)_minmax(300px,0.7fr)]">
        <!-- 7-Day Completion Trend Interactive Bar Chart -->
        <AnimatedBarChart :trend="stats.completion_trend || []" />

        <!-- Status & Priority Breakdown Card -->
        <div class="surface-card flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
              <h2 class="section-title">Ledger Distribution</h2>
              <AppIcon name="tasks" :size="18" class="text-slate-400" />
            </div>

            <!-- Status Breakdown -->
            <div class="mt-4 space-y-2.5">
              <span class="data-label block">By Status</span>
              <div
                v-for="item in stats.status_breakdown || []"
                :key="item.label"
                class="flex items-center justify-between rounded-xl bg-slate-50 p-2.5 transition-colors hover:bg-slate-100 dark:bg-night-surface dark:hover:bg-slate-850"
              >
                <div class="flex items-center gap-2">
                  <span
                    class="h-2 w-2 rounded-full"
                    :class="item.label === 'done' ? 'bg-emerald-500' : item.label === 'in_progress' ? 'bg-amber-500' : 'bg-slate-400'"
                  ></span>
                  <span class="text-xs font-semibold capitalize text-slate-700 dark:text-slate-300">
                    {{ item.label.replace('_', ' ') }}
                  </span>
                </div>
                <span class="font-mono text-xs font-bold text-slate-900 dark:text-white">
                  <AnimatedNumber :value="item.count" />
                </span>
              </div>
            </div>

            <!-- Priority Breakdown -->
            <div class="mt-5 space-y-2.5">
              <span class="data-label block">By Priority</span>
              <div
                v-for="item in stats.priority_breakdown || []"
                :key="item.label"
                class="flex items-center justify-between rounded-xl bg-slate-50 p-2.5 transition-colors hover:bg-slate-100 dark:bg-night-surface dark:hover:bg-slate-850"
              >
                <div class="flex items-center gap-2">
                  <span
                    class="h-2 w-2 rounded-full"
                    :class="item.label === 'high' ? 'bg-rose-500' : item.label === 'medium' ? 'bg-amber-500' : 'bg-slate-400'"
                  ></span>
                  <span class="text-xs font-semibold capitalize text-slate-700 dark:text-slate-300">
                    {{ item.label }}
                  </span>
                </div>
                <span class="font-mono text-xs font-bold text-slate-900 dark:text-white">
                  <AnimatedNumber :value="item.count" />
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Study Velocity Heatmap & Streak Matrix -->
      <StudyHeatmap :tasks="taskStore.items" :stats="stats" class="mt-8" />
    </template>

    <!-- Quick Task Creation Modal -->
    <TaskModal
      :is-open="isCreateTaskOpen"
      :projects="projectStore.items"
      :loading="creatingTaskLoading"
      :form-errors="taskFormErrors"
      @close="isCreateTaskOpen = false"
      @save="handleCreateTask"
    />
  </div>
</template>
