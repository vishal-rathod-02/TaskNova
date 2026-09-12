<script setup>
import { computed, onMounted, ref } from "vue";
import AppIcon from "../components/AppIcon.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import { useAnalyticsStore } from "../stores/analytics";
import { useAuthStore } from "../stores/auth";
import { useNotificationStore } from "../stores/notifications";

const analyticsStore = useAnalyticsStore();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const error = ref("");

const stats = computed(() => analyticsStore.stats || {});
const trendMax = computed(() => Math.max(...(stats.value.completion_trend || []).map((item) => item.count), 1));
const isEmpty = computed(() => !analyticsStore.loading && !authStore.isAdmin && stats.value.total_tasks === 0);
const report = computed(() => notificationStore.latestReport);

const loadDashboard = async () => {
  error.value = "";
  try {
    await Promise.all([
      analyticsStore.fetchStats(authStore.isAdmin),
      authStore.isAdmin ? Promise.resolve() : notificationStore.fetchNotifications(),
      authStore.isAdmin ? Promise.resolve() : notificationStore.fetchLatestReport().catch(() => {}),
    ]);
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to load dashboard data.";
  }
};

onMounted(loadDashboard);
</script>

<template>
  <div class="page-shell">
    <PageHeader
      :title="authStore.isAdmin ? 'System overview' : `Good to see you, ${authStore.user?.full_name?.split(' ')[0] || 'there'}.`"
      :description="authStore.isAdmin ? 'A concise read on accounts, project activity, and system-wide task health.' : 'A clear read on the work in front of you.'"
    >
      <template #actions>
        <router-link v-if="!authStore.isAdmin" class="btn-primary gap-2" to="/tasks"><AppIcon name="plus" :size="16" />Create task</router-link>
        <button class="btn-secondary gap-2" type="button" :disabled="analyticsStore.loading" @click="loadDashboard"><AppIcon name="refresh" :size="16" />{{ analyticsStore.loading ? "Refreshing..." : "Refresh" }}</button>
      </template>
    </PageHeader>
    <p v-if="analyticsStore.stats" class="data-label mt-4">Updated from {{ analyticsStore.source === 'cache' ? 'cached snapshot' : 'live database' }}</p>

    <section
      v-if="!authStore.isAdmin && notificationStore.unreadCount"
      class="mt-6 flex flex-wrap items-center gap-x-4 gap-y-2 border border-ember/40 bg-white px-5 py-4 dark:border-ember-dark/50 dark:bg-night-surface"
      aria-live="polite"
    >
      <AppIcon name="alert" :size="20" class="text-ember dark:text-ember-dark" />
      <p class="text-sm text-ink dark:text-[#E7E9ED]">
        <strong class="font-semibold">{{ notificationStore.unreadCount }} unread reminder{{ notificationStore.unreadCount === 1 ? "" : "s" }}</strong>
        from the deadline job. Review what needs attention.
      </p>
      <router-link class="ml-auto min-h-11 px-1 py-2 text-sm font-medium text-ink underline decoration-slate/50 underline-offset-4 hover:decoration-ink dark:text-[#E7E9ED]" to="/notifications">Open inbox</router-link>
    </section>

    <p v-if="error" class="field-error mt-5" aria-live="polite">{{ error }}</p>
    <p v-if="analyticsStore.loading && !analyticsStore.stats" class="mt-12 text-sm text-slate dark:text-[#9AA3B2]">Loading your current account of work...</p>

    <section v-else-if="authStore.isAdmin" class="mt-10 grid border-t border-slate/20 sm:grid-cols-2 lg:grid-cols-4 dark:border-slate/30">
      <article class="metric-block border-r-0 px-0 sm:px-5 sm:first:pl-0 lg:border-r lg:border-slate/20 dark:lg:border-slate/30">
        <p class="data-label">Active users</p><p class="metric-number">{{ stats.active_users || 0 }}</p><p class="mt-1 text-sm text-slate dark:text-[#9AA3B2]">of {{ stats.total_users || 0 }} accounts</p>
      </article>
      <article class="metric-block border-r-0 px-0 sm:px-5 lg:border-r lg:border-slate/20 dark:lg:border-slate/30">
        <p class="data-label">Projects</p><p class="metric-number">{{ stats.total_projects || 0 }}</p><p class="mt-1 text-sm text-slate dark:text-[#9AA3B2]">system-wide</p>
      </article>
      <article class="metric-block border-r-0 px-0 sm:px-5 lg:border-r lg:border-slate/20 dark:lg:border-slate/30">
        <p class="data-label">Overdue tasks</p><p class="metric-number text-ember dark:text-ember-dark">{{ stats.overdue_tasks || 0 }}</p><p class="mt-1 text-sm text-slate dark:text-[#9AA3B2]">need attention</p>
      </article>
      <article class="metric-block px-0 sm:px-5 sm:last:pr-0">
        <p class="data-label">Activity, 24h</p><p class="metric-number">{{ stats.activity_last_24h || 0 }}</p><p class="mt-1 text-sm text-slate dark:text-[#9AA3B2]">recorded changes</p>
      </article>
    </section>

    <EmptyState
      v-else-if="isEmpty"
      class="mt-12"
      title="No tasks yet"
      description="Create your first project, then add the next piece of work you want to track."
    >
      <template #actions>
        <router-link class="btn-primary gap-2" to="/projects"><AppIcon name="plus" :size="16" />Create your first project</router-link>
      </template>
    </EmptyState>

    <template v-else-if="!authStore.isAdmin">
      <section v-if="report" class="surface mt-10 flex flex-wrap items-baseline gap-x-8 gap-y-2 px-5 py-4">
        <div>
          <p class="data-label">Latest daily report · {{ report.report_date }}</p>
          <p class="mt-1 text-sm text-ink dark:text-[#E7E9ED]">{{ report.completed_tasks }} of {{ report.total_tasks }} done, {{ report.overdue_tasks }} overdue.</p>
        </div>
        <router-link class="ml-auto min-h-11 px-1 py-2 text-sm font-medium text-ink underline decoration-slate/50 underline-offset-4 hover:decoration-ink dark:text-[#E7E9ED]" to="/notifications">How this was generated</router-link>
      </section>

      <section class="mt-10 grid border-t border-slate/20 sm:grid-cols-2 lg:grid-cols-4 dark:border-slate/30">
        <article class="metric-block border-r-0 px-0 sm:px-5 sm:first:pl-0 lg:border-r lg:border-slate/20 dark:lg:border-slate/30"><p class="data-label">Open tasks</p><p class="metric-number">{{ (stats.total_tasks || 0) - (stats.completed_tasks || 0) }}</p></article>
        <article class="metric-block border-r-0 px-0 sm:px-5 lg:border-r lg:border-slate/20 dark:lg:border-slate/30"><p class="data-label">Completed</p><p class="metric-number text-ledger-green dark:text-ledger-greenDark">{{ stats.completed_tasks || 0 }}</p></article>
        <article class="metric-block border-r-0 px-0 sm:px-5 lg:border-r lg:border-slate/20 dark:lg:border-slate/30"><p class="data-label">Overdue</p><p class="metric-number text-ember dark:text-ember-dark">{{ stats.overdue_tasks || 0 }}</p></article>
        <article class="metric-block px-0 sm:px-5 sm:last:pr-0"><p class="data-label">Completion</p><p class="metric-number">{{ stats.completion_rate || 0 }}%</p></article>
      </section>

      <section class="mt-12 grid gap-10 lg:grid-cols-[minmax(0,1.2fr)_minmax(280px,0.8fr)]">
        <article>
          <h2 class="section-title">Completed over seven days</h2>
          <p class="mt-2 body-copy">Each mark records a status change to done.</p>
          <div class="mt-8 flex h-44 items-end gap-2 border-b border-slate/30 pb-1 dark:border-slate/40">
            <div v-for="item in stats.completion_trend || []" :key="item.date" class="flex h-full min-w-0 flex-1 flex-col justify-end gap-2">
              <span class="data-label truncate text-center">{{ item.count }}</span>
              <div class="min-h-[4px] bg-ink dark:bg-[#E7E9ED]" :style="{ height: `${Math.max((item.count / trendMax) * 100, 3)}%` }"></div>
              <span class="data-label truncate text-center">{{ new Date(`${item.date}T00:00:00`).toLocaleDateString(undefined, { weekday: 'short' }) }}</span>
            </div>
          </div>
        </article>
        <article>
          <h2 class="section-title">Status account</h2>
          <div class="mt-5 border-t border-slate/20 dark:border-slate/30">
            <div v-for="item in stats.status_breakdown || []" :key="item.label" class="flex items-center justify-between border-b border-slate/20 py-4 dark:border-slate/30"><span class="text-sm capitalize text-ink dark:text-[#E7E9ED]">{{ item.label.replace('_', ' ') }}</span><span class="data-label">{{ item.count }}</span></div>
          </div>
          <h2 class="section-title mt-8">Priority account</h2>
          <div class="mt-5 border-t border-slate/20 dark:border-slate/30">
            <div v-for="item in stats.priority_breakdown || []" :key="item.label" class="flex items-center justify-between border-b border-slate/20 py-4 dark:border-slate/30"><span class="text-sm capitalize text-ink dark:text-[#E7E9ED]">{{ item.label }}</span><span class="data-label">{{ item.count }}</span></div>
          </div>
        </article>
      </section>
    </template>
  </div>
</template>
