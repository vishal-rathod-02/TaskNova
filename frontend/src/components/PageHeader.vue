<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: "" },
});
</script>

<template>
  <header class="flex flex-wrap items-end justify-between gap-6 border-b border-slate/20 pb-8 dark:border-slate/30">
    <div class="min-w-0">
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="description" class="mt-2 body-copy">{{ description }}</p>
    </div>
    <div class="flex flex-wrap gap-3">
      <slot name="actions" />
    </div>
  </header>
</template>
