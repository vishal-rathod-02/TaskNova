<script setup>
import AppIcon from "./AppIcon.vue";

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: "" },
  icon: { type: String, default: "sparkles" },
});
</script>

<template>
  <div class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white/50 p-8 text-center backdrop-blur-sm dark:border-slate-800 dark:bg-night-card/40 sm:p-12">
    <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 shadow-sm dark:bg-brand-950/60 dark:text-brand-300">
      <AppIcon :name="icon" :size="28" />
    </div>
    <h3 class="font-display mt-4 text-lg font-bold text-slate-900 dark:text-white">{{ title }}</h3>
    <p v-if="description" class="body-copy mt-2 max-w-md text-center">{{ description }}</p>
    <div v-if="$slots.actions" class="mt-6 flex flex-wrap items-center justify-center gap-3">
      <slot name="actions" />
    </div>
  </div>
</template>
