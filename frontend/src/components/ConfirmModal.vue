<script setup>
import { watch } from "vue";
import AppIcon from "./AppIcon.vue";

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  title: { type: String, default: "Are you sure?" },
  message: { type: String, default: "This action cannot be undone." },
  confirmText: { type: String, default: "Confirm" },
  cancelText: { type: String, default: "Cancel" },
  isDanger: { type: Boolean, default: true },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(["confirm", "cancel"]);

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
  },
  { immediate: true }
);
</script>

<template>
  <Teleport to="body">
    <!-- Rigid Backdrop: Clicking outside does NOT close -->
    <div v-if="isOpen" class="modal-backdrop z-50 animate-fade-in">
      <div class="modal-panel max-w-md animate-scale-in" role="dialog" aria-modal="true">
        <div class="flex items-start gap-4">
          <div
            :class="isDanger ? 'bg-rose-100 text-rose-600 dark:bg-rose-950/60 dark:text-rose-400' : 'bg-brand-100 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300'"
            class="flex h-12 w-12 flex-none items-center justify-center rounded-2xl"
          >
            <AppIcon :name="isDanger ? 'alert' : 'info'" :size="24" />
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="font-display text-lg font-bold text-slate-900 dark:text-white">{{ title }}</h3>
            <p class="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-400">{{ message }}</p>
          </div>
        </div>
        <div class="mt-6 flex flex-wrap items-center justify-end gap-3">
          <button
            type="button"
            class="btn-secondary"
            :disabled="loading"
            @click="emit('cancel')"
          >
            {{ cancelText }}
          </button>
          <button
            type="button"
            :class="isDanger ? 'btn-danger' : 'btn-primary'"
            :disabled="loading"
            @click="emit('confirm')"
          >
            <span v-if="loading" class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
            {{ loading ? "Processing..." : confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
