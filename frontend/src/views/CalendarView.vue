<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import AppIcon from "../components/AppIcon.vue";
import AppLoader from "../components/AppLoader.vue";
import PageHeader from "../components/PageHeader.vue";
import SkeletonLoader from "../components/SkeletonLoader.vue";
import TaskCalendar from "../components/TaskCalendar.vue";
import TaskDetailModal from "../components/TaskDetailModal.vue";
import TaskModal from "../components/TaskModal.vue";
import { showToast } from "../composables/toast";
import { useAuthStore } from "../stores/auth";
import { useProjectStore } from "../stores/projects";
import { useTaskStore } from "../stores/tasks";
import { withMinLoading } from "../utils/async";
import { exportTasksToCSV, exportTasksToICS, printAcademicLedger } from "../utils/export";

const authStore = useAuthStore();
const projectStore = useProjectStore();
const taskStore = useTaskStore();

const error = ref("");
const isExportOpen = ref(false);
const exportMenuRef = ref(null);

// Live Calendar Feed Modal State
const isSyncModalOpen = ref(false);
const isRegenerating = ref(false);

const onDocClick = (e) => {
  if (exportMenuRef.value && !exportMenuRef.value.contains(e.target)) {
    isExportOpen.value = false;
  }
};

if (typeof document !== "undefined") {
  document.addEventListener("click", onDocClick);
}

onBeforeUnmount(() => {
  if (typeof document !== "undefined") {
    document.removeEventListener("click", onDocClick);
  }
});

// Task Modal State
const isTaskModalOpen = ref(false);
const isEditMode = ref(false);
const selectedTask = ref(null);
const taskModalLoading = ref(false);
const formErrors = ref({});

// Detail Modal State
const isTaskDetailOpen = ref(false);
const detailTaskId = ref(null);

const hasProjects = computed(() => projectStore.items.length > 0);

const loadCalendarData = async () => {
  error.value = "";
  try {
    await withMinLoading(
      Promise.all([
        projectStore.fetchProjects(),
        taskStore.fetchTasks(),
        authStore.fetchCurrentUser(),
      ]),
      1800
    );
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to load calendar schedules.";
  }
};

const openDetail = (task) => {
  detailTaskId.value = task.id;
  isTaskDetailOpen.value = true;
};

const handleAddTaskOnDate = (dateStr) => {
  isEditMode.value = false;
  selectedTask.value = {
    project_id: projectStore.items[0]?.id || "",
    status: "todo",
    due_date: `${dateStr}T18:00:00`,
  };
  formErrors.value = {};
  isTaskModalOpen.value = true;
};

const openCreateModal = () => {
  isEditMode.value = false;
  selectedTask.value = {
    project_id: projectStore.items[0]?.id || "",
    status: "todo",
    priority: "medium",
  };
  formErrors.value = {};
  isTaskModalOpen.value = true;
};

const openEditModal = (task) => {
  isEditMode.value = true;
  selectedTask.value = { ...task };
  formErrors.value = {};
  isTaskModalOpen.value = true;
};

const handleSaveTask = async (formData) => {
  taskModalLoading.value = true;
  formErrors.value = {};
  error.value = "";

  try {
    const toUtcIso = (localInput) => (localInput ? new Date(localInput).toISOString() : null);
    const payload = {
      ...formData,
      project_id: Number(formData.project_id),
      due_date: toUtcIso(formData.due_date),
    };

    if (isEditMode.value) {
      await taskStore.updateTask(selectedTask.value.id, payload);
      showToast("Assignment updated in calendar.");
    } else {
      await taskStore.createTask(payload);
      showToast("Assignment scheduled on academic calendar.");
    }
    isTaskModalOpen.value = false;
    await taskStore.fetchTasks();
  } catch (requestError) {
    formErrors.value = requestError.response?.data?.errors || {};
    error.value = requestError.response?.data?.message || "Unable to save task.";
  } finally {
    taskModalLoading.value = false;
  }
};

const copyFeedUrl = async (url, label) => {
  try {
    await navigator.clipboard.writeText(url);
    showToast(`${label} copied to clipboard!`);
  } catch {
    showToast("Failed to copy URL to clipboard.");
  }
};

const handleRegenerateToken = async () => {
  if (!confirm("Regenerating your token will invalidate any existing calendar subscriptions on your devices. Continue?")) {
    return;
  }
  isRegenerating.value = true;
  try {
    await authStore.regenerateCalendarToken();
    showToast("Private calendar feed token renewed.");
  } catch (err) {
    showToast(err.response?.data?.message || "Failed to regenerate token.");
  } finally {
    isRegenerating.value = false;
  }
};

onMounted(loadCalendarData);
</script>

<template>
  <div class="page-shell">
    <!-- Header -->
    <PageHeader
      title="Academic Calendar"
      description="Visualize deadlines, exam schedules, and course milestones across your semester."
      badge="Semester Schedule"
    >
      <template #actions>
        <!-- Export & Live Sync Dropdown with Click-Outside and Transition -->
        <div ref="exportMenuRef" class="relative w-full sm:w-auto">
          <button
            class="btn-secondary min-h-11 w-full justify-center gap-2 sm:w-auto"
            type="button"
            :aria-expanded="isExportOpen"
            @click="isExportOpen = !isExportOpen"
          >
            <AppIcon name="sparkles" :size="16" class="flex-none" />
            <span>Export & Sync</span>
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
              class="absolute right-0 top-full mt-2 w-72 max-w-[calc(100vw-2rem)] rounded-2xl border border-slate-200/90 bg-white/95 p-1.5 shadow-2xl backdrop-blur-xl z-50 dark:border-slate-800 dark:bg-night-surface/95 origin-top-right"
            >
              <div class="px-3 py-2 border-b border-slate-100 dark:border-slate-800/80 mb-1">
                <span class="text-[10px] font-mono font-bold tracking-wider uppercase text-slate-400">Live Sync & Exports</span>
              </div>

              <!-- Live WebCal Subscription Option -->
              <button
                type="button"
                class="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs font-semibold text-brand-700 bg-brand-50/70 hover:bg-brand-100/80 dark:bg-brand-950/40 dark:text-brand-300 dark:hover:bg-brand-900/60 transition-colors mb-1"
                @click="isSyncModalOpen = true; isExportOpen = false"
              >
                <span class="flex items-center gap-2.5">
                  <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-500 text-white shadow-sm">
                    <AppIcon name="sparkles" :size="14" />
                  </span>
                  <span class="text-left">
                    <span class="block font-bold">Subscribe Live Calendar</span>
                    <span class="text-[10px] opacity-75 font-normal">Apple, Google & Outlook feed</span>
                  </span>
                </span>
                <span class="font-mono text-[10px] uppercase font-bold text-brand-600 dark:text-brand-400">Live</span>
              </button>

              <button
                type="button"
                class="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
                @click="exportTasksToICS(taskStore.items, 'TaskNova Academic Schedule'); isExportOpen = false"
              >
                <span class="flex items-center gap-2.5">
                  <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300">
                    <AppIcon name="calendar" :size="15" />
                  </span>
                  <span>Static iCalendar File</span>
                </span>
                <span class="font-mono text-[10px] text-slate-400">.ics</span>
              </button>

              <button
                type="button"
                class="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
                @click="exportTasksToCSV(taskStore.items, 'tasknova-calendar-schedule.csv'); isExportOpen = false"
              >
                <span class="flex items-center gap-2.5">
                  <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-300">
                    <AppIcon name="list" :size="15" />
                  </span>
                  <span>CSV Spreadsheet</span>
                </span>
                <span class="font-mono text-[10px] text-slate-400">.csv</span>
              </button>

              <button
                type="button"
                class="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
                @click="printAcademicLedger(taskStore.items, 'Academic Calendar Schedule'); isExportOpen = false"
              >
                <span class="flex items-center gap-2.5">
                  <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-300">
                    <AppIcon name="info" :size="15" />
                  </span>
                  <span>Print Schedule</span>
                </span>
                <span class="font-mono text-[10px] text-slate-400">PDF / Print</span>
              </button>
            </div>
          </transition>
        </div>

        <button
          class="btn-primary min-h-11 w-full justify-center gap-2 sm:w-auto"
          type="button"
          :disabled="!hasProjects"
          @click="openCreateModal"
        >
          <AppIcon name="plus" :size="16" class="flex-none" /> Schedule Task
        </button>
      </template>
    </PageHeader>

    <p v-if="!hasProjects" class="field-help mt-4">
      Create a <router-link class="font-bold text-brand-600 underline dark:text-brand-400" to="/projects">course/project</router-link> before scheduling calendar assignments.
    </p>

    <!-- Error Alert -->
    <p v-if="error" class="field-error mt-6" aria-live="polite">
      <AppIcon name="alert" :size="16" /> {{ error }}
    </p>

    <!-- Main Calendar Content -->
    <section class="mt-8">
      <div v-if="taskStore.loading" class="space-y-6">
        <SkeletonLoader type="board" :count="4" />
        <AppLoader size="md" text="Rendering academic calendar schedule" />
      </div>

      <TaskCalendar
        v-else
        :tasks="taskStore.items"
        :projects="projectStore.items"
        @open-detail="openDetail"
        @add-task-on-date="handleAddTaskOnDate"
        @edit="openEditModal"
      />
    </section>

    <!-- Live Calendar Feed Subscription Modal -->
    <div
      v-if="isSyncModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in"
      @click.self="isSyncModalOpen = false"
    >
      <div class="w-full max-w-lg rounded-3xl border border-slate-200/90 bg-white/95 p-6 shadow-2xl backdrop-blur-xl dark:border-slate-800 dark:bg-night-surface/95 sm:p-8 space-y-6">
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-950/70 dark:text-brand-300">
              <AppIcon name="sparkles" :size="22" />
            </div>
            <div>
              <h2 class="text-xl font-extrabold text-slate-900 dark:text-white">Live Calendar Subscription</h2>
              <p class="text-xs text-slate-500 dark:text-slate-400">Sync all coursework & assignments seamlessly with your calendar app</p>
            </div>
          </div>
          <button
            type="button"
            class="rounded-xl p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-200"
            @click="isSyncModalOpen = false"
          >
            <AppIcon name="close" :size="18" />
          </button>
        </div>

        <div class="space-y-4">
          <!-- WebCal Instant Link -->
          <div class="rounded-2xl border border-brand-200/80 bg-brand-50/50 p-4 dark:border-brand-900/40 dark:bg-brand-950/20">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold uppercase tracking-wider text-brand-700 dark:text-brand-300">1-Click Apple / Outlook Subscribe</span>
              <span class="rounded-full bg-brand-100 px-2.5 py-0.5 text-[10px] font-bold text-brand-700 dark:bg-brand-900/60 dark:text-brand-300">Auto-updating</span>
            </div>
            <p class="text-xs text-slate-600 dark:text-slate-300 mb-3">
              Subscribes your device's native calendar to live changes. Any updated deadlines update automatically.
            </p>
            <div class="flex flex-wrap items-center gap-2">
              <a
                :href="authStore.webcalFeedUrl"
                class="btn-primary py-2 px-4 text-xs font-bold gap-2"
                target="_blank"
                rel="noreferrer"
              >
                <AppIcon name="calendar" :size="14" /> Open in Calendar App
              </a>
              <button
                type="button"
                class="btn-secondary py-2 px-3 text-xs font-semibold gap-1.5"
                @click="copyFeedUrl(authStore.webcalFeedUrl, 'WebCal subscription link')"
              >
                <AppIcon name="check" :size="14" /> Copy WebCal URL
              </button>
            </div>
          </div>

          <!-- Google Calendar / Standard HTTPS URL -->
          <div class="rounded-2xl border border-slate-200/80 bg-slate-50/70 p-4 dark:border-slate-800 dark:bg-slate-900/40">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">Google Calendar URL Subscription</span>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mb-2">
              In Google Calendar &rarr; Other calendars &rarr; <strong>From URL</strong>, paste this private HTTPS URL:
            </p>
            <div class="flex items-center gap-2">
              <input
                type="text"
                readonly
                :value="authStore.calendarFeedUrl"
                class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs font-mono text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-300 select-all"
                @focus="$event.target.select()"
              />
              <button
                type="button"
                class="btn-secondary flex-none py-2 px-3 text-xs font-semibold"
                @click="copyFeedUrl(authStore.calendarFeedUrl, 'Google Calendar feed link')"
              >
                Copy
              </button>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
          <button
            type="button"
            class="text-rose-600 hover:text-rose-700 dark:text-rose-400 hover:underline font-semibold"
            :disabled="isRegenerating"
            @click="handleRegenerateToken"
          >
            {{ isRegenerating ? "Regenerating..." : "Revoke & Renew Private Feed Token" }}
          </button>
          <button
            type="button"
            class="btn-secondary py-1.5 px-4 text-xs font-bold"
            @click="isSyncModalOpen = false"
          >
            Done
          </button>
        </div>
      </div>
    </div>

    <!-- Task Create / Edit Modal -->
    <TaskModal
      :is-open="isTaskModalOpen"
      :is-edit="isEditMode"
      :task-data="selectedTask"
      :projects="projectStore.items"
      :loading="taskModalLoading"
      :form-errors="formErrors"
      @close="isTaskModalOpen = false"
      @save="handleSaveTask"
    />

    <!-- Dedicated Task Detail Modal -->
    <TaskDetailModal
      :is-open="isTaskDetailOpen"
      :task-id="detailTaskId"
      @close="isTaskDetailOpen = false; taskStore.fetchTasks()"
      @edit="isTaskDetailOpen = false; openEditModal($event)"
    />
  </div>
</template>
