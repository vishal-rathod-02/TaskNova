<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: "" },
  badge: { type: String, default: "" },
});
</script>

<template>
  <header class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
    <div>
      <div class="flex flex-wrap items-center gap-2.5">
        <h1 class="page-title">{{ title }}</h1>
        <span
          v-if="badge"
          class="rounded-full bg-brand-50 px-2.5 py-0.5 font-mono text-xs font-bold text-brand-700 dark:bg-brand-950/60 dark:text-brand-300 border border-brand-200 dark:border-brand-900/50"
        >
          {{ badge }}
        </span>
      </div>
      <p v-if="description" class="mt-1.5 body-copy">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="flex flex-wrap items-center gap-2.5">
      <slot name="actions" />
    </div>
  </header>
</template>
