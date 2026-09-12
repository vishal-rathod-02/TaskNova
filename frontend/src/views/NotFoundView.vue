<script setup>
import AppIcon from "../components/AppIcon.vue";
import PageHeader from "../components/PageHeader.vue";
</script>

<template>
  <div class="page-shell">
    <PageHeader title="Page not found" description="This entry is not in the ledger. The address may be mistyped or the page may have moved.">
      <template #actions>
        <router-link class="btn-primary gap-2" to="/"><AppIcon name="dashboard" :size="16" />Back to dashboard</router-link>
        <router-link class="btn-secondary gap-2" to="/tasks"><AppIcon name="tasks" :size="16" />View tasks</router-link>
      </template>
    </PageHeader>
    <p class="data-label mt-8">Error 404 · {{ $route.fullPath }}</p>
  </div>
</template>
