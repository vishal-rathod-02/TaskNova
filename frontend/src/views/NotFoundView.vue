<script setup>
import AppIcon from "../components/AppIcon.vue";
</script>

<template>
  <div class="page-shell flex min-h-[60vh] flex-col items-center justify-center text-center">
    <div class="surface-card max-w-md p-8 text-center">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-950 dark:text-brand-300 shadow-sm">
        <AppIcon name="academic" :size="32" />
      </div>
      <h1 class="font-display mt-5 text-3xl font-extrabold text-slate-900 dark:text-white">Page Not Found</h1>
      <p class="mt-2 text-xs leading-relaxed text-slate-500 dark:text-slate-400">
        The course page, assignment, or resource you are looking for does not exist in this workspace ledger.
      </p>
      <div class="mt-6 flex flex-wrap items-center justify-center gap-3">
        <router-link to="/" class="btn-primary gap-2">
          <AppIcon name="dashboard" :size="16" /> Return to Dashboard
        </router-link>
      </div>
    </div>
  </div>
</template>
