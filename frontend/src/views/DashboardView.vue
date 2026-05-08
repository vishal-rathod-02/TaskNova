<script setup>
import { onMounted } from "vue";
import { useAnalyticsStore } from "../stores/analytics";
import { useAuthStore } from "../stores/auth";

const analyticsStore = useAnalyticsStore();
const authStore = useAuthStore();

onMounted(async () => {
  await analyticsStore.fetchStats();
});
</script>

<template>
  <div class="page-wrap">
    <section class="panel title-row">
      <div>
        <h2 class="section-title">Productivity Dashboard</h2>
        <p class="section-subtitle">Welcome back, {{ authStore.user?.full_name }}.</p>
      </div>
      <span class="chip">{{ authStore.user?.role }}</span>
    </section>

    <section class="grid grid-3">
      <article class="panel">
        <p class="section-subtitle">Total Tasks</p>
        <h2 style="margin: 8px 0 0">{{ analyticsStore.stats?.total_tasks || 0 }}</h2>
      </article>
      <article class="panel">
        <p class="section-subtitle">Completed</p>
        <h2 style="margin: 8px 0 0">{{ analyticsStore.stats?.completed_tasks || 0 }}</h2>
      </article>
      <article class="panel">
        <p class="section-subtitle">Overdue</p>
        <h2 style="margin: 8px 0 0">{{ analyticsStore.stats?.overdue_tasks || 0 }}</h2>
      </article>
    </section>

    <section class="panel">
      <h3 class="section-title">Status Breakdown</h3>
      <div class="grid grid-3">
        <div v-for="item in analyticsStore.statusBreakdown" :key="item.status" class="panel">
          <strong style="text-transform: capitalize">{{ item.status }}</strong>
          <p class="muted">{{ item.count }} tasks</p>
        </div>
      </div>
    </section>
  </div>
</template>
