<script setup>
import { reactive, ref } from "vue";
import AppIcon from "./AppIcon.vue";

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  preview: { type: Object, default: null },
  previewLoading: { type: Boolean, default: false },
  applyLoading: { type: Boolean, default: false },
  formErrors: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["preview", "apply", "close"]);

const todayIso = () => {
  const d = new Date();
  const pad = (v) => String(v).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
};

const form = reactive({
  date: todayIso(),
  work_start: "09:00",
  work_end: "17:00",
  mode: "maker",
  max_tasks: 6,
});

const requestPreview = () => emit("preview", { ...form, max_tasks: Number(form.max_tasks) });
const requestApply = () => emit("apply", { ...form, max_tasks: Number(form.max_tasks) });

const modeHelp = ref({
  maker: "90-minute deep work blocks with short buffers between sessions.",
  pomodoro: "25-minute sprints with 5-minute cognitive breaks.",
});
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-backdrop z-50 animate-fade-in overflow-y-auto">
      <div class="modal-panel my-auto flex max-h-[92vh] w-full max-w-xl animate-scale-in flex-col overflow-hidden p-4 sm:p-6" role="dialog" aria-modal="true">
        <div class="flex flex-none items-start justify-between gap-3 border-b border-slate-100 pb-3 dark:border-slate-800 sm:pb-4">
          <div class="flex min-w-0 flex-1 items-center gap-2.5 sm:gap-3">
            <div class="flex h-9 w-9 flex-none items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300 sm:h-10 sm:w-10">
              <AppIcon name="sparkles" :size="19" />
            </div>
            <div class="min-w-0 flex-1">
              <h2 class="truncate font-display text-base font-bold text-slate-900 dark:text-white sm:text-lg">Plan My Day</h2>
              <p class="truncate text-[11px] text-slate-500 dark:text-slate-400 sm:text-xs">Auto-fit pending tasks into open focus windows.</p>
            </div>
          </div>
          <button type="button" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white" @click="$emit('close')" aria-label="Close">
            <AppIcon name="x" :size="18" />
          </button>
        </div>

        <div class="mt-4 flex-1 space-y-4 overflow-y-auto pr-0.5">
          <div class="grid gap-4 sm:grid-cols-3">
            <div>
              <label class="field-label" for="plan-date">Date</label>
              <input id="plan-date" v-model="form.date" type="date" class="input-field" />
              <p v-if="formErrors.date" class="field-error">{{ formErrors.date }}</p>
            </div>
            <div>
              <label class="field-label" for="plan-start">Work starts</label>
              <input id="plan-start" v-model="form.work_start" type="time" class="input-field" />
            </div>
            <div>
              <label class="field-label" for="plan-end">Work ends</label>
              <input id="plan-end" v-model="form.work_end" type="time" class="input-field" />
            </div>
          </div>
          <p v-if="formErrors.work_start" class="field-error">{{ formErrors.work_start }}</p>

          <div>
            <span class="field-label">Work style</span>
            <div class="grid grid-cols-2 gap-2.5">
              <button
                v-for="mode in ['maker', 'pomodoro']"
                :key="mode"
                type="button"
                class="rounded-xl border px-3 py-2.5 text-left text-xs font-bold capitalize transition-all"
                :class="form.mode === mode
                  ? 'border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-950/60 dark:text-brand-300'
                  : 'border-slate-200 text-slate-500 hover:border-slate-300 dark:border-slate-700 dark:text-slate-400'"
                @click="form.mode = mode"
              >
                {{ mode }}
                <span class="mt-1 block text-[11px] font-medium normal-case opacity-80">{{ modeHelp[mode] }}</span>
              </button>
            </div>
            <p v-if="formErrors.mode" class="field-error">{{ formErrors.mode }}</p>
          </div>

          <button type="button" class="btn-secondary w-full" :disabled="previewLoading" @click="requestPreview">
            <span v-if="previewLoading" class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
            {{ previewLoading ? "Scanning backlog…" : "Preview Schedule" }}
          </button>

          <div v-if="preview" class="space-y-2.5">
            <p class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Proposed plan · {{ preview.proposal?.length || 0 }} block(s)
            </p>
            <div v-if="!preview.proposal?.length" class="surface-card p-4 text-sm text-slate-500 dark:text-slate-400">
              No open windows for {{ preview.date }} — try a wider work window or move a fixed block.
            </div>
            <div
              v-for="item in preview.proposal"
              :key="item.task_id"
              class="surface-card flex items-center justify-between gap-3 p-3"
            >
              <div class="min-w-0">
                <p class="truncate text-sm font-bold text-slate-900 dark:text-white">{{ item.title }}</p>
                <p class="font-mono text-[11px] text-slate-500 dark:text-slate-400">
                  {{ item.start_time }} – {{ item.end_time }} · {{ item.priority }}
                </p>
              </div>
              <span class="flex-none rounded-lg bg-brand-50 px-2 py-1 font-mono text-[11px] font-bold text-brand-700 dark:bg-brand-950/60 dark:text-brand-300">
                {{ item.project_name || "No project" }}
              </span>
            </div>
            <p v-if="preview.unscheduled?.length" class="text-xs text-slate-500 dark:text-slate-400">
              {{ preview.unscheduled.length }} task(s) did not fit and stay in the backlog.
            </p>
          </div>
        </div>

        <div class="mt-4 flex flex-none flex-col-reverse gap-2.5 border-t border-slate-100 pt-4 dark:border-slate-800 sm:flex-row sm:justify-end">
          <button type="button" class="btn-secondary" :disabled="applyLoading" @click="$emit('close')">Close</button>
          <button type="button" class="btn-primary" :disabled="!preview?.proposal?.length || applyLoading" @click="requestApply">
            <span v-if="applyLoading" class="inline-block h-4 w-4 flex-none animate-spin rounded-full border-2 border-current border-t-transparent"></span>
            <span class="truncate">{{ applyLoading ? "Applying…" : "Apply Schedule" }}</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
