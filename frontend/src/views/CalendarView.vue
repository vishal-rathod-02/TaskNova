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
import { useProjectStore } from "../stores/projects";
import { useTaskStore } from "../stores/tasks";
import { withMinLoading } from "../utils/async";
import { exportTasksToCSV, exportTasksToICS, printAcademicLedger } from "../utils/export";

const projectStore = useProjectStore();
const taskStore = useTaskStore();

const error = ref("");
const isExportOpen = ref(false);
const exportMenuRef = ref(null);

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
        <!-- Export Dropdown with Click-Outside and Transition -->
        <div ref="exportMenuRef" class="relative">
          <button
            class="btn-secondary gap-2"
            type="button"
            :aria-expanded="isExportOpen"
            @click="isExportOpen = !isExportOpen"
          >
            <AppIcon name="sparkles" :size="16" />
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
              class="absolute right-0 top-full mt-2 w-64 rounded-2xl border border-slate-200/90 bg-white/95 p-1.5 shadow-2xl backdrop-blur-xl z-40 dark:border-slate-800 dark:bg-night-surface/95"
            >
              <div class="px-3 py-2 border-b border-slate-100 dark:border-slate-800/80 mb-1">
                <span class="text-[10px] font-mono font-bold tracking-wider uppercase text-slate-400">Export Options</span>
              </div>

              <button
                type="button"
                class="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
                @click="exportTasksToICS(taskStore.items, 'TaskNova Academic Schedule'); isExportOpen = false"
              >
                <span class="flex items-center gap-2.5">
                  <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300">
                    <AppIcon name="calendar" :size="15" />
                  </span>
                  <span>Sync iCalendar</span>
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
          class="btn-primary gap-2"
          type="button"
          :disabled="!hasProjects"
          @click="openCreateModal"
        >
          <AppIcon name="plus" :size="16" /> Schedule Task
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
