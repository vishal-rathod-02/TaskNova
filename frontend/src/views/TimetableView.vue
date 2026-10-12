<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import AppIcon from "../components/AppIcon.vue";
import ConfirmModal from "../components/ConfirmModal.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import PlanMyDayModal from "../components/PlanMyDayModal.vue";
import SkeletonLoader from "../components/SkeletonLoader.vue";
import TimetableSlotModal from "../components/TimetableSlotModal.vue";
import { showToast } from "../composables/toast";
import { TEMPLATES, useTimetableStore } from "../stores/timetable";
import { useProjectStore } from "../stores/projects";
import { withMinLoading } from "../utils/async";
import { exportTimetableToCSV, exportTimetableToICS, printTimetableAgenda } from "../utils/export";

const timetableStore = useTimetableStore();
const projectStore = useProjectStore();

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const WEEKDAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

const TYPE_STYLES = {
  meeting: "border-l-violet-500",
  focus_work: "border-l-brand-500",
  operations: "border-l-amber-500",
  habit: "border-l-emerald-500",
  personal: "border-l-cyan-500",
};

const error = ref("");
const viewMode = ref("week"); // 'week' | 'today'
const showWeekend = ref(false);
const selectedDate = ref("");
const nowMin = ref(0);
let clockTimer = null;

// Slot modal state
const isSlotModalOpen = ref(false);
const isEditMode = ref(false);
const selectedSlot = ref(null);
const slotModalLoading = ref(false);
const slotFormErrors = ref({});

// Delete state
const isDeleteOpen = ref(false);
const pendingDeleteId = ref(null);
const deleteLoading = ref(false);

// Plan My Day state
const isPlanOpen = ref(false);
const planPreview = ref(null);
const previewLoading = ref(false);
const applyLoading = ref(false);
const planErrors = ref({});

// Template state
const templateChoice = ref("corporate");
const templateLoading = ref(false);

// Export dropdown state
const isExportOpen = ref(false);
const exportMenuRef = ref(null);

const onExportDocClick = (e) => {
  if (exportMenuRef.value && !exportMenuRef.value.contains(e.target)) {
    isExportOpen.value = false;
  }
};

if (typeof document !== "undefined") {
  document.addEventListener("click", onExportDocClick);
}

const dayAgendaLabel = computed(() => {
  const iso = selectedDate.value || todayIso();
  return WEEKDAYS_FULL[weekdayOf(iso)] + ", " + iso;
});

const pad = (v) => String(v).padStart(2, "0");

// A saved custom color wins over the block-type default. Only strict hex is
// applied inline so legacy palette tokens can never inject arbitrary CSS.
const isHexColor = (value) => /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(String(value || ""));
const slotBorderStyle = (slot) => (isHexColor(slot.color_override) ? { borderLeftColor: slot.color_override } : {});
const todayIso = () => {
  const d = new Date();
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
};
const toMinutes = (hhmm) => {
  const [h, m] = String(hhmm || "00:00").split(":").map(Number);
  return h * 60 + m;
};
// Backend convention: 0=Mon..6=Sun.
const weekdayOf = (iso) => (new Date(`${iso}T12:00:00`).getDay() + 6) % 7;

const visibleDays = computed(() => (showWeekend.value ? [0, 1, 2, 3, 4, 5, 6] : [0, 1, 2, 3, 4]));
const todayWeekday = computed(() => weekdayOf(todayIso()));
const selectedWeekday = computed(() => (selectedDate.value ? weekdayOf(selectedDate.value) : todayWeekday.value));

const todaySlots = computed(() => timetableStore.slotsForDate(selectedDate.value || todayIso()));

// Chronological timeline with a live "Now" divider inserted before the first
// block that has not ended yet (only meaningful for the current date).
const isViewingToday = computed(() => (selectedDate.value || todayIso()) === todayIso());
const timelineItems = computed(() => {
  const items = [];
  let dividerInserted = false;
  for (const slot of todaySlots.value) {
    if (isViewingToday.value && !dividerInserted && toMinutes(slot.end_time) > nowMin.value) {
      items.push({ kind: "now" });
      dividerInserted = true;
    }
    items.push({ kind: "slot", slot });
  }
  return items;
});

const nextCommitment = computed(() => {
  const upcoming = todaySlots.value.find((s) => toMinutes(s.end_time) > nowMin.value);
  if (!upcoming) return null;
  const startsIn = toMinutes(upcoming.start_time) - nowMin.value;
  return { slot: upcoming, startsIn };
});

const refreshClock = () => {
  const now = new Date();
  nowMin.value = now.getHours() * 60 + now.getMinutes();
};

const loadTimetable = async () => {
  error.value = "";
  try {
    await withMinLoading(
      Promise.all([
        timetableStore.fetchSlots(),
        projectStore.fetchProjects(),
        timetableStore.fetchAvailableTemplates(),
      ]),
      1200
    );
    // If the previously chosen template was retired mid-session, fall back silently.
    if (!pickerTemplates.value.some((t) => t.value === templateChoice.value)) {
      templateChoice.value = pickerTemplates.value[0]?.value || "";
    }
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to load timetable.";
  }
};

// Enabled-only picker: disabled templates never appear (no blunt "blocked" UX).
const pickerTemplates = computed(() => {
  const live = (timetableStore.availableTemplates || []).map((t) => ({
    value: t.name || t.value,
    label: t.label || t.name || t.value,
  }));
  return live.length ? live : TEMPLATES;
});

const extractErrors = (requestError) => requestError.response?.data?.errors || {};

onMounted(() => {
  selectedDate.value = todayIso();
  refreshClock();
  clockTimer = setInterval(refreshClock, 60000);
  loadTimetable();
});

onBeforeUnmount(() => {
  if (clockTimer) clearInterval(clockTimer);
  if (typeof document !== "undefined") {
    document.removeEventListener("click", onExportDocClick);
  }
});

// ---- Slot CRUD ----
const openCreateModal = (prefill = {}) => {
  isEditMode.value = false;
  selectedSlot.value = { ...prefill };
  slotFormErrors.value = {};
  isSlotModalOpen.value = true;
};

const openEditModal = (slot) => {
  isEditMode.value = true;
  selectedSlot.value = { ...slot };
  slotFormErrors.value = {};
  isSlotModalOpen.value = true;
};

const handleSaveSlot = async (payload) => {
  slotModalLoading.value = true;
  slotFormErrors.value = {};
  try {
    if (isEditMode.value) {
      await timetableStore.updateSlot(selectedSlot.value.id, payload);
      showToast("Routine block updated.", "success");
    } else {
      await timetableStore.createSlot(payload);
      showToast("Routine block created.", "success");
    }
    isSlotModalOpen.value = false;
  } catch (requestError) {
    if (requestError.response?.status === 409) {
      const conflict = requestError.response.data?.conflict;
      showToast(
        conflict
          ? `Overlaps "${conflict.title}" (${conflict.start_time}–${conflict.end_time}).`
          : "Time slot overlaps an existing entry.",
        "error"
      );
    } else {
      slotFormErrors.value = extractErrors(requestError);
      if (!Object.keys(slotFormErrors.value).length) {
        error.value = requestError.response?.data?.message || "Unable to save routine block.";
      }
    }
  } finally {
    slotModalLoading.value = false;
  }
};

const askDelete = (id) => {
  pendingDeleteId.value = id;
  isDeleteOpen.value = true;
};

const handleDelete = async () => {
  deleteLoading.value = true;
  try {
    await timetableStore.deleteSlot(pendingDeleteId.value);
    showToast("Routine block deleted.", "success");
    isDeleteOpen.value = false;
  } catch (requestError) {
    showToast(requestError.response?.data?.message || "Unable to delete routine block.", "error");
  } finally {
    deleteLoading.value = false;
  }
};

// ---- Templates ----
const handleApplyTemplate = async () => {
  templateLoading.value = true;
  try {
    const days = showWeekend.value ? [0, 1, 2, 3, 4, 5, 6] : [0, 1, 2, 3, 4];
    const result = await timetableStore.applyTemplate({ template: templateChoice.value, days });
    const made = result.created?.length || 0;
    const skipped = result.skipped?.length || 0;
    showToast(
      made ? `Template applied: ${made} block(s) added${skipped ? `, ${skipped} skipped (overlap)` : ""}.` : "All template blocks already exist — nothing added.",
      made ? "success" : "info"
    );
  } catch (requestError) {
    if (requestError.response?.status === 403) {
      // Template retired mid-session: refresh the picker so it vanishes quietly.
      await timetableStore.fetchAvailableTemplates().catch(() => {});
      templateChoice.value = pickerTemplates.value[0]?.value || "";
      showToast("This routine template is not available yet.", "info");
    } else {
      showToast(requestError.response?.data?.message || "Unable to apply template.", "error");
    }
  } finally {
    templateLoading.value = false;
  }
};

// ---- Plan My Day ----
const openPlanModal = () => {
  planPreview.value = null;
  planErrors.value = {};
  isPlanOpen.value = true;
};

const handlePreview = async (payload) => {
  previewLoading.value = true;
  planErrors.value = {};
  try {
    planPreview.value = await timetableStore.previewDay(payload);
  } catch (requestError) {
    planErrors.value = extractErrors(requestError);
    if (!Object.keys(planErrors.value).length) {
      showToast(requestError.response?.data?.message || "Unable to preview schedule.", "error");
    }
  } finally {
    previewLoading.value = false;
  }
};

const handleApplyPlan = async (payload) => {
  applyLoading.value = true;
  try {
    const result = await timetableStore.applyDay(payload);
    const made = result.created?.length || 0;
    showToast(made ? `Daily plan applied: ${made} focus block(s) scheduled.` : "Nothing to apply — no open windows.", made ? "success" : "info");
    if (made) {
      isPlanOpen.value = false;
      selectedDate.value = result.date;
      viewMode.value = "today";
    }
  } catch (requestError) {
    showToast(requestError.response?.data?.message || "Unable to apply schedule.", "error");
  } finally {
    applyLoading.value = false;
  }
};

const shiftSelectedDate = (delta) => {
  const d = new Date(`${selectedDate.value}T12:00:00`);
  d.setDate(d.getDate() + delta);
  selectedDate.value = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
};

const formatCountdown = (mins) => {
  if (mins <= 0) return "starting now";
  if (mins < 60) return `in ${mins} min`;
  return `in ${Math.floor(mins / 60)}h ${mins % 60}m`;
};

const handlePrintDay = () => {
  isExportOpen.value = false;
  if (!todaySlots.value.length) {
    showToast("No blocks on the selected date to print.", "info");
    return;
  }
  printTimetableAgenda(todaySlots.value, "day", dayAgendaLabel.value);
};
</script>

<template>
  <div class="mx-auto max-w-7xl px-3.5 py-5 sm:px-6 sm:py-8">
    <PageHeader
      title="Timetable & Daily Routine"
      description="Block fixed commitments and let Plan My Day fit deep work around them."
      :badge="`${timetableStore.items.length} blocks`"
    >
      <template #actions>
        <div ref="exportMenuRef" class="relative">
          <button
            class="btn-secondary gap-2"
            type="button"
            :disabled="!timetableStore.items.length"
            :aria-expanded="isExportOpen"
            @click="isExportOpen = !isExportOpen"
          >
            <AppIcon name="printer" :size="16" />
            <span>Export</span>
            <AppIcon name="chevron" :size="14" class="text-slate-400 transition-transform duration-200" :class="{ 'rotate-180': isExportOpen }" />
          </button>
          <transition
            enter-active-class="transition duration-150 ease-out"
            enter-from-class="transform scale-95 opacity-0 -translate-y-1"
            enter-to-class="transform scale-100 opacity-100 translate-y-0"
            leave-active-class="transition duration-100 ease-in"
            leave-from-class="transform scale-100 opacity-100 translate-y-0"
            leave-to-class="transform scale-95 opacity-0 -translate-y-1"
          >
            <div
              v-if="isExportOpen"
              class="absolute right-0 top-full z-50 mt-2 w-72 max-w-[calc(100vw-2rem)] origin-top-right rounded-2xl border border-slate-200/90 bg-white/95 p-1.5 shadow-2xl backdrop-blur-xl dark:border-slate-800 dark:bg-night-surface/95"
            >
              <div class="mb-1 border-b border-slate-100 px-3 py-2 dark:border-slate-800/80">
                <span class="font-mono text-[10px] font-bold uppercase tracking-wider text-slate-400">Print & Exports</span>
              </div>
              <button
                type="button"
                class="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
                @click="printTimetableAgenda(timetableStore.items, 'week', 'Monday – Sunday'); isExportOpen = false"
              >
                <span class="flex items-center gap-2.5">
                  <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-300">
                    <AppIcon name="printer" :size="15" />
                  </span>
                  <span>Print Weekly Grid</span>
                </span>
                <span class="font-mono text-[10px] text-slate-400">PDF / Print</span>
              </button>
              <button
                type="button"
                class="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
                @click="handlePrintDay"
              >
                <span class="flex items-center gap-2.5">
                  <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-300">
                    <AppIcon name="list" :size="15" />
                  </span>
                  <span>Print Day Agenda</span>
                </span>
                <span class="font-mono text-[10px] text-slate-400">PDF / Print</span>
              </button>
              <button
                type="button"
                class="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
                @click="exportTimetableToICS(timetableStore.items, 'TaskNova Weekly Routine'); isExportOpen = false"
              >
                <span class="flex items-center gap-2.5">
                  <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300">
                    <AppIcon name="calendar" :size="15" />
                  </span>
                  <span>Calendar File</span>
                </span>
                <span class="font-mono text-[10px] text-slate-400">.ics</span>
              </button>
              <button
                type="button"
                class="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
                @click="exportTimetableToCSV(timetableStore.items, 'tasknova-timetable.csv'); isExportOpen = false"
              >
                <span class="flex items-center gap-2.5">
                  <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-300">
                    <AppIcon name="grid" :size="15" />
                  </span>
                  <span>CSV Spreadsheet</span>
                </span>
                <span class="font-mono text-[10px] text-slate-400">.csv</span>
              </button>
            </div>
          </transition>
        </div>
        <button class="btn-secondary gap-2" type="button" :disabled="timetableStore.loading" @click="loadTimetable">
          <AppIcon name="refresh" :size="16" :class="{ 'animate-spin': timetableStore.loading }" />
          {{ timetableStore.loading ? "Refreshing..." : "Refresh" }}
        </button>
        <button class="btn-secondary gap-2" type="button" @click="openPlanModal">
          <AppIcon name="sparkles" :size="16" />
          Plan My Day
        </button>
        <button class="btn-primary gap-2" type="button" @click="openCreateModal()">
          <AppIcon name="plus" :size="16" />
          New Block
        </button>
      </template>
    </PageHeader>

    <!-- Error notice -->
    <p v-if="error" class="field-error mt-4" aria-live="polite">
      <AppIcon name="alert" :size="16" /> {{ error }}
    </p>

    <!-- Controls: view mode, work-week scope, persona template -->
    <div class="mt-6 flex flex-wrap items-center gap-2.5">
      <div class="flex rounded-xl border border-slate-200 bg-white p-1 dark:border-slate-700 dark:bg-night-surface">
        <button
          type="button"
          class="rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all"
          :class="viewMode === 'week' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-500 dark:text-slate-400'"
          @click="viewMode = 'week'"
        >
          Week
        </button>
        <button
          type="button"
          class="rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all"
          :class="viewMode === 'today' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-500 dark:text-slate-400'"
          @click="viewMode = 'today'"
        >
          Today
        </button>
      </div>

      <button
        v-if="viewMode === 'week'"
        type="button"
        class="rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-bold text-slate-600 transition-all dark:border-slate-700 dark:bg-night-surface dark:text-slate-300"
        @click="showWeekend = !showWeekend"
      >
        {{ showWeekend ? "Mon–Fri only" : "Include weekend" }}
      </button>

      <div class="flex flex-1 flex-wrap items-center justify-end gap-2.5">
        <select v-model="templateChoice" class="input-field w-auto text-xs font-semibold" aria-label="Persona template">
          <option v-for="tpl in pickerTemplates" :key="tpl.value" :value="tpl.value">{{ tpl.label }}</option>
        </select>
        <button class="btn-secondary gap-2 !py-2 text-xs" type="button" :disabled="templateLoading" @click="handleApplyTemplate">
          <span v-if="templateLoading" class="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
          {{ templateLoading ? "Applying..." : "Apply Template" }}
        </button>
      </div>
    </div>

    <!-- Loading State with Skeleton only (no spinner to avoid double-loader flash) -->
    <div v-if="timetableStore.loading && !timetableStore.items.length" class="mt-8 space-y-6">
      <SkeletonLoader type="board" :count="4" />
    </div>

    <template v-else>
      <!-- Weekly master grid -->
      <section v-if="viewMode === 'week'" class="mt-6">
        <div v-if="!timetableStore.items.length">
          <EmptyState
            class="mt-2"
            icon="timetable"
            title="No routine blocks yet"
            description="Apply a persona template or create your first block to build the weekly rhythm."
          >
            <template #actions>
              <button class="btn-secondary" type="button" :disabled="templateLoading" @click="handleApplyTemplate">{{ templateLoading ? "Applying..." : `Apply ${pickerTemplates.find((t) => t.value === templateChoice)?.label || "Template"}` }}</button>
              <button class="btn-primary" type="button" @click="openCreateModal()">Create Block</button>
            </template>
          </EmptyState>
        </div>
        <div v-else class="grid gap-4 sm:grid-cols-2" :class="visibleDays.length > 5 ? 'xl:grid-cols-7 lg:grid-cols-4' : 'lg:grid-cols-5'">
          <div
            v-for="dow in visibleDays"
            :key="dow"
            class="flex min-h-40 flex-col rounded-2xl border border-slate-200/80 bg-slate-100/40 p-3 dark:border-slate-800 dark:bg-night-surface/50"
          >
            <div class="flex items-center justify-between px-1 pb-2">
              <p class="font-display text-sm font-bold text-slate-800 dark:text-slate-100">
                {{ WEEKDAYS[dow] }}
                <span v-if="dow === todayWeekday" class="ml-1.5 rounded-full bg-brand-600 px-2 py-0.5 font-mono text-[10px] font-bold text-white">Today</span>
              </p>
              <button
                type="button"
                class="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-white hover:text-brand-600 dark:hover:bg-slate-800"
                :title="`Add block on ${WEEKDAYS_FULL[dow]}`"
                @click="openCreateModal({ prefill_day: dow })"
              >
                <AppIcon name="plus" :size="15" />
              </button>
            </div>
            <div class="flex flex-1 flex-col gap-2">
              <div
                v-for="slot in timetableStore.slotsForDay(dow)"
                :key="slot.id"
                class="surface-card cursor-pointer border-l-4 p-3 transition-all hover:-translate-y-0.5"
                :class="TYPE_STYLES[slot.slot_type] || 'border-l-brand-500'"
                :style="slotBorderStyle(slot)"
                @click="openEditModal(slot)"
              >
                <p class="truncate text-[13px] font-bold text-slate-900 dark:text-white">{{ slot.title }}</p>
                <p class="mt-0.5 font-mono text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                  {{ slot.start_time }} – {{ slot.end_time }}
                </p>
                <p v-if="slot.location || slot.project_name" class="mt-0.5 truncate text-[11px] text-slate-500 dark:text-slate-400">
                  {{ [slot.project_name, slot.location].filter(Boolean).join(" · ") }}
                </p>
              </div>
              <button
                v-if="!timetableStore.slotsForDay(dow).length"
                type="button"
                class="flex flex-1 items-center justify-center rounded-xl border border-dashed border-slate-300 py-6 text-[11px] font-semibold text-slate-400 transition-colors hover:border-brand-400 hover:text-brand-600 dark:border-slate-700"
                @click="openCreateModal({ prefill_day: dow })"
              >
                + Add block
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Daily execution timeline -->
      <section v-else class="mt-6">
        <div class="flex flex-wrap items-center gap-2.5">
          <button type="button" class="btn-secondary !px-3 !py-2" @click="shiftSelectedDate(-1)" aria-label="Previous day">
            <AppIcon name="chevron-left" :size="16" />
          </button>
          <input v-model="selectedDate" type="date" class="input-field w-auto" aria-label="Select date" />
          <button type="button" class="btn-secondary !px-3 !py-2" @click="shiftSelectedDate(1)" aria-label="Next day">
            <AppIcon name="chevron-right" :size="16" />
          </button>
          <button type="button" class="btn-secondary !py-2 text-xs" @click="selectedDate = todayIso()">Today</button>
          <span class="font-mono text-xs font-bold text-slate-500 dark:text-slate-400">
            {{ WEEKDAYS_FULL[selectedWeekday] }}
          </span>
        </div>

        <!-- Next-commitment countdown -->
        <div
          v-if="nextCommitment"
          class="mt-4 flex items-center gap-3 rounded-2xl border border-brand-200 bg-brand-50/70 px-4 py-3 dark:border-brand-900/50 dark:bg-brand-950/40"
          role="status"
        >
          <span class="relative flex h-2.5 w-2.5 flex-none">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-500 opacity-60"></span>
            <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-brand-600"></span>
          </span>
          <p class="text-sm font-semibold text-brand-900 dark:text-brand-200">
            Next: {{ nextCommitment.slot.title }}
            <span class="font-mono text-xs opacity-80">
              {{ formatCountdown(nextCommitment.startsIn) }} · {{ nextCommitment.slot.start_time }}{{ nextCommitment.slot.location ? ` · ${nextCommitment.slot.location}` : "" }}
            </span>
          </p>
        </div>
        <div
          v-else-if="todaySlots.length"
          class="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50/70 px-4 py-3 text-sm font-semibold text-emerald-900 dark:border-emerald-900/50 dark:bg-emerald-950/40 dark:text-emerald-200"
          role="status"
        >
          Day complete — no remaining blocks.
        </div>

        <div v-if="!todaySlots.length" class="mt-4">
          <EmptyState
            icon="timetable"
            title="Open day — nothing scheduled"
            description="Create a block for this date or run Plan My Day to fill it from the backlog."
          >
            <template #actions>
              <button class="btn-secondary" type="button" @click="openPlanModal">Plan My Day</button>
              <button class="btn-primary" type="button" @click="openCreateModal({ prefill_date: selectedDate })">Add Block</button>
            </template>
          </EmptyState>
        </div>

        <ol v-else class="relative mt-5 space-y-3 border-l-2 border-slate-200 pl-5 dark:border-slate-700">
          <template v-for="(item, index) in timelineItems" :key="item.kind === 'now' ? `now-${index}` : item.slot.id">
            <li
              v-if="item.kind === 'now'"
              class="relative flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-rose-500"
              aria-hidden="true"
            >
              <span class="absolute -left-[27px] h-2.5 w-2.5 rounded-full bg-rose-500 shadow-glow-sm"></span>
              <span class="h-0.5 flex-1 rounded bg-gradient-to-r from-rose-500 to-transparent"></span>
              Now · {{ pad(Math.floor(nowMin / 60)) }}:{{ pad(nowMin % 60) }}
            </li>
            <li
              v-else
              class="surface-card cursor-pointer border-l-4 p-4"
              :class="TYPE_STYLES[item.slot.slot_type] || 'border-l-brand-500'"
              :style="slotBorderStyle(item.slot)"
              @click="openEditModal(item.slot)"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="truncate font-display text-sm font-bold text-slate-900 dark:text-white">{{ item.slot.title }}</p>
                  <p class="mt-1 font-mono text-xs font-semibold text-slate-500 dark:text-slate-400">
                    {{ item.slot.start_time }} – {{ item.slot.end_time }} · {{ item.slot.duration_minutes }} min
                  </p>
                  <p v-if="item.slot.location || item.slot.project_name" class="mt-0.5 truncate text-xs text-slate-500 dark:text-slate-400">
                    {{ [item.slot.project_name, item.slot.location].filter(Boolean).join(" · ") }}
                  </p>
                </div>
                <div class="flex flex-none items-center gap-1.5" @click.stop>
                  <button type="button" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white" title="Edit block" @click="openEditModal(item.slot)">
                    <AppIcon name="edit" :size="15" />
                  </button>
                  <button type="button" class="rounded-lg p-1.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/40 dark:hover:text-rose-400" title="Delete block" @click="askDelete(item.slot.id)">
                    <AppIcon name="trash" :size="15" />
                  </button>
                </div>
              </div>
            </li>
          </template>
        </ol>
      </section>
    </template>

    <!-- Slot modal -->
    <TimetableSlotModal
      :is-open="isSlotModalOpen"
      :is-edit="isEditMode"
      :slot-data="selectedSlot"
      :projects="projectStore.items"
      :loading="slotModalLoading"
      :form-errors="slotFormErrors"
      @save="handleSaveSlot"
      @close="isSlotModalOpen = false"
    />

    <!-- Plan My Day modal -->
    <PlanMyDayModal
      :is-open="isPlanOpen"
      :preview="planPreview"
      :preview-loading="previewLoading"
      :apply-loading="applyLoading"
      :form-errors="planErrors"
      @preview="handlePreview"
      @apply="handleApplyPlan"
      @close="isPlanOpen = false"
    />

    <!-- Delete confirm -->
    <ConfirmModal
      :is-open="isDeleteOpen"
      title="Delete routine block?"
      message="This removes the block from the weekly routine. Allocations on it are removed too."
      confirm-text="Delete Block"
      :loading="deleteLoading"
      @confirm="handleDelete"
      @cancel="isDeleteOpen = false"
      @close="isDeleteOpen = false"
    />
  </div>
</template>
