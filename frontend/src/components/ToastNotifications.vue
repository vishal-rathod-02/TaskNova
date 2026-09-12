<script setup>
import AppIcon from "./AppIcon.vue";
import { dismissToast, toastState } from "../composables/toast";
</script>

<template>
  <div class="fixed right-4 top-16 z-50 grid w-[min(360px,calc(100vw-2rem))] gap-2 md:top-4" aria-live="polite" aria-atomic="true">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toastState.items"
        :key="toast.id"
        :class="toast.type === 'error' ? 'border-ember bg-white text-ember dark:bg-night-surface dark:text-ember-dark' : 'border-ledger-green bg-white text-ledger-green dark:bg-night-surface dark:text-ledger-greenDark'"
        class="flex items-center justify-between gap-4 border px-4 py-3 text-sm shadow-sm"
      >
        <span class="flex items-center gap-2"><AppIcon :name="toast.type === 'error' ? 'info' : 'check'" :size="16" />{{ toast.message }}</span>
        <button class="min-h-11 px-1 text-xs font-medium underline" type="button" aria-label="Dismiss notification" @click="dismissToast(toast.id)">Dismiss</button>
      </div>
    </TransitionGroup>
  </div>
</template>
