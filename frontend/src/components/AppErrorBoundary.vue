<script setup>
import { onErrorCaptured, ref } from "vue";
import AppIcon from "./AppIcon.vue";

const hasError = ref(false);
const errorMessage = ref("");

onErrorCaptured((err) => {
  hasError.value = true;
  errorMessage.value = err?.message || "An unexpected error occurred.";
  return false;
});

const reload = () => {
  window.location.reload();
};
</script>

<template>
  <div v-if="hasError" class="page-shell flex min-h-[50vh] flex-col items-center justify-center text-center">
    <div class="surface-card max-w-md p-8 text-center">
      <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-100 text-rose-600 dark:bg-rose-950 dark:text-rose-400">
        <AppIcon name="alert" :size="28" />
      </div>
      <h2 class="font-display mt-4 text-xl font-bold text-slate-900 dark:text-white">Workspace View Error</h2>
      <p class="mt-2 text-xs leading-relaxed text-slate-500 dark:text-slate-400">{{ errorMessage }}</p>
      <button class="btn-primary mt-6 w-full" type="button" @click="reload">
        <AppIcon name="refresh" :size="16" /> Reload Workspace
      </button>
    </div>
  </div>
  <slot v-else />
</template>
