<script setup>
import { computed, reactive, watch } from "vue";
import AppIcon from "./AppIcon.vue";
import { SLOT_TYPES, SLOT_TYPE_LABELS } from "../stores/timetable";

// Friendly named palette — no hex knowledge required. Values stay backend-compatible.
const PRESET_COLORS = [
  { hex: "#800020", name: "Burgundy" },
  { hex: "#e11d48", name: "Rose" },
  { hex: "#ea580c", name: "Orange" },
  { hex: "#d97706", name: "Amber" },
  { hex: "#16a34a", name: "Green" },
  { hex: "#0d9488", name: "Teal" },
  { hex: "#0284c7", name: "Sky" },
  { hex: "#4f46e5", name: "Indigo" },
  { hex: "#8b5cf6", name: "Violet" },
  { hex: "#64748b", name: "Slate" },
];

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  isEdit: { type: Boolean, default: false },
  slotData: { type: Object, default: () => ({}) },
  projects: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  formErrors: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["save", "close"]);

const WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

const form = reactive({
  title: "",
  slot_type: "focus_work",
  is_recurring: true,
  day_of_week: 0,
  specific_date: "",
  start_time: "09:00",
  end_time: "10:00",
  location: "",
  color_override: "",
  project_id: "",
});

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      document.body.style.overflow = "hidden";
      const src = props.slotData || {};
      form.title = src.title || "";
      form.slot_type = src.slot_type || "focus_work";
      form.is_recurring = src.is_recurring !== false;
      form.day_of_week = src.day_of_week ?? src.prefill_day ?? 0;
      form.specific_date = src.specific_date || src.prefill_date || "";
      form.start_time = src.start_time || "09:00";
      form.end_time = src.end_time || "10:00";
      form.location = src.location || "";
      form.color_override = src.color_override || "";
      form.project_id = src.project_id || "";
    } else {
      document.body.style.overflow = "";
    }
  },
  { immediate: true }
);

const selectedColorName = computed(() => {
  const found = PRESET_COLORS.find((c) => c.hex.toLowerCase() === String(form.color_override).toLowerCase());
  if (found) return found.name;
  if (form.color_override) return "Custom";
  return "Type default";
});

// Native color input requires #rrggbb; normalize anything else to a safe fallback.
const customColor = computed({
  get: () => (/^#[0-9a-fA-F]{6}$/.test(form.color_override) ? form.color_override : "#4f46e5"),
  set: (value) => {
    form.color_override = value;
  },
});

const submitForm = () => {
  const payload = {
    title: form.title,
    slot_type: form.slot_type,
    is_recurring: form.is_recurring,
    start_time: form.start_time,
    end_time: form.end_time,
    location: form.location || null,
    color_override: form.color_override || null,
    project_id: form.project_id === "" ? null : Number(form.project_id),
  };
  if (form.is_recurring) {
    payload.day_of_week = Number(form.day_of_week);
    payload.specific_date = null;
  } else {
    payload.day_of_week = null;
    payload.specific_date = form.specific_date || null;
  }
  emit("save", payload);
};
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-backdrop z-50 animate-fade-in overflow-y-auto">
      <div class="modal-panel my-auto flex max-h-[92vh] w-full max-w-xl animate-scale-in flex-col overflow-hidden p-4 sm:p-6" role="dialog" aria-modal="true">
        <div class="flex flex-none items-start justify-between gap-3 border-b border-slate-100 pb-3 dark:border-slate-800 sm:pb-4">
          <div class="flex min-w-0 flex-1 items-center gap-2.5 sm:gap-3">
            <div class="flex h-9 w-9 flex-none items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300 sm:h-10 sm:w-10">
              <AppIcon name="timetable" :size="19" />
            </div>
            <div class="min-w-0 flex-1">
              <h2 class="truncate font-display text-base font-bold text-slate-900 dark:text-white sm:text-lg">
                {{ isEdit ? "Edit Routine Block" : "New Routine Block" }}
              </h2>
              <p class="truncate text-[11px] text-slate-500 dark:text-slate-400 sm:text-xs">
                {{ isEdit ? "Update this timetable entry." : "Block time for meetings, focus work, or habits." }}
              </p>
            </div>
          </div>
          <button type="button" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white" @click="$emit('close')" aria-label="Close">
            <AppIcon name="x" :size="18" />
          </button>
        </div>

        <div class="mt-4 flex-1 space-y-4 overflow-y-auto pr-0.5">
          <div>
            <label class="field-label" for="slot-title">Title</label>
            <input id="slot-title" v-model="form.title" type="text" class="input-field" placeholder="e.g. Daily Standup, Deep Work, Gym" maxlength="160" />
            <p v-if="formErrors.title" class="field-error">{{ formErrors.title }}</p>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label class="field-label" for="slot-type">Block type</label>
              <select id="slot-type" v-model="form.slot_type" class="input-field">
                <option v-for="type in SLOT_TYPES" :key="type" :value="type">{{ SLOT_TYPE_LABELS[type] }}</option>
              </select>
              <p v-if="formErrors.slot_type" class="field-error">{{ formErrors.slot_type }}</p>
            </div>
            <div>
              <label class="field-label" for="slot-project">Linked project (optional)</label>
              <select id="slot-project" v-model="form.project_id" class="input-field">
                <option value="">No link</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">{{ project.name }}</option>
              </select>
              <p v-if="formErrors.project_id" class="field-error">{{ formErrors.project_id }}</p>
            </div>
          </div>

          <label class="flex cursor-pointer items-center justify-between rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm font-semibold dark:border-slate-700">
            <span>Repeat weekly</span>
            <input v-model="form.is_recurring" type="checkbox" class="h-4 w-4 accent-indigo-600" />
          </label>

          <div v-if="form.is_recurring">
            <label class="field-label" for="slot-day">Day of week</label>
            <select id="slot-day" v-model="form.day_of_week" class="input-field">
              <option v-for="(day, index) in WEEKDAYS" :key="day" :value="index">{{ day }}</option>
            </select>
            <p v-if="formErrors.day_of_week" class="field-error">{{ formErrors.day_of_week }}</p>
          </div>
          <div v-else>
            <label class="field-label" for="slot-date">Specific date</label>
            <input id="slot-date" v-model="form.specific_date" type="date" class="input-field" />
            <p v-if="formErrors.specific_date" class="field-error">{{ formErrors.specific_date }}</p>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label class="field-label" for="slot-start">Start time</label>
              <input id="slot-start" v-model="form.start_time" type="time" class="input-field" />
              <p v-if="formErrors.start_time" class="field-error">{{ formErrors.start_time }}</p>
            </div>
            <div>
              <label class="field-label" for="slot-end">End time</label>
              <input id="slot-end" v-model="form.end_time" type="time" class="input-field" />
              <p v-if="formErrors.end_time" class="field-error">{{ formErrors.end_time }}</p>
            </div>
          </div>

          <div>
            <label class="field-label" for="slot-location">Location (optional)</label>
            <input id="slot-location" v-model="form.location" type="text" class="input-field" placeholder="Zoom, Boardroom B…" maxlength="200" />
            <p v-if="formErrors.location" class="field-error">{{ formErrors.location }}</p>
          </div>

          <div>
            <span id="slot-color-label" class="field-label">Accent color · {{ selectedColorName }}</span>
            <div class="flex flex-wrap items-center gap-2" role="group" aria-labelledby="slot-color-label">
              <button
                type="button"
                class="flex h-8 min-w-8 items-center justify-center rounded-full border border-dashed border-slate-300 px-2 font-mono text-[10px] font-bold text-slate-400 transition-all hover:border-slate-400 dark:border-slate-600"
                :class="{ 'ring-2 ring-brand-500 ring-offset-2 dark:ring-offset-slate-900': !form.color_override }"
                title="Use block-type default color"
                @click="form.color_override = ''"
              >
                A
              </button>
              <button
                v-for="preset in PRESET_COLORS"
                :key="preset.hex"
                type="button"
                class="h-8 w-8 rounded-full transition-transform hover:scale-110"
                :style="{ backgroundColor: preset.hex }"
                :class="{ 'ring-2 ring-brand-500 ring-offset-2 dark:ring-offset-slate-900': form.color_override?.toLowerCase() === preset.hex }"
                :title="preset.name"
                :aria-label="preset.name"
                @click="form.color_override = preset.hex"
              />
              <label
                class="relative h-8 w-8 cursor-pointer overflow-hidden rounded-full transition-transform hover:scale-110"
                :style="{ background: `conic-gradient(#e11d48, #d97706, #16a34a, #0284c7, #8b5cf6, #e11d48)` }"
                title="Pick a custom color"
              >
                <span class="sr-only">Pick a custom color</span>
                <input v-model="customColor" type="color" class="absolute inset-0 h-full w-full cursor-pointer opacity-0" aria-label="Pick a custom color" />
              </label>
            </div>
            <p v-if="formErrors.color_override" class="field-error">{{ formErrors.color_override }}</p>
          </div>
        </div>

        <div class="mt-4 flex flex-none flex-col-reverse gap-2.5 border-t border-slate-100 pt-4 dark:border-slate-800 sm:flex-row sm:justify-end">
          <button type="button" class="btn-secondary" :disabled="loading" @click="$emit('close')">Cancel</button>
          <button type="button" class="btn-primary" :disabled="loading" @click="submitForm">
            <span v-if="loading" class="inline-block h-4 w-4 flex-none animate-spin rounded-full border-2 border-current border-t-transparent"></span>
            <span class="truncate">{{ loading ? "Saving..." : (isEdit ? "Save Changes" : "Create Block") }}</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
