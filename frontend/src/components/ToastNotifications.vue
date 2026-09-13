<script setup>
import AppIcon from "./AppIcon.vue";
import { dismissToast, toastState } from "../composables/toast";
</script>

<template>
  <div class="fixed right-4 top-20 z-50 grid w-[min(380px,calc(100vw-2rem))] gap-2.5 sm:top-6" aria-live="polite" aria-atomic="true">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toastState.items"
        :key="toast.id"
        :class="toast.type === 'error'
          ? 'border-rose-300 bg-white text-rose-800 shadow-glow-urgent dark:border-rose-900/60 dark:bg-night-surface dark:text-rose-300'
          : 'border-emerald-300 bg-white text-emerald-800 shadow-glow-success dark:border-emerald-900/60 dark:bg-night-surface dark:text-emerald-300'"
        class="flex items-center justify-between gap-3 rounded-2xl border p-4 text-xs font-semibold shadow-xl backdrop-blur-lg"
      >
        <div class="flex items-center gap-2.5">
          <div
            :class="toast.type === 'error' ? 'bg-rose-100 text-rose-600 dark:bg-rose-950 dark:text-rose-400' : 'bg-emerald-100 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400'"
            class="flex h-7 w-7 flex-none items-center justify-center rounded-lg"
          >
            <AppIcon :name="toast.type === 'error' ? 'alert' : 'check-circle'" :size="16" />
          </div>
          <span class="leading-snug">{{ toast.message }}</span>
        </div>
        <button
          class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
          type="button"
          aria-label="Dismiss notification"
          @click="dismissToast(toast.id)"
        >
          <AppIcon name="x" :size="14" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
