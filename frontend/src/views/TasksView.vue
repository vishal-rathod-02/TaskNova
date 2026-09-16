<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import AppIcon from "../components/AppIcon.vue";
import AppLoader from "../components/AppLoader.vue";
import ConfirmModal from "../components/ConfirmModal.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import SkeletonLoader from "../components/SkeletonLoader.vue";
import TaskCard from "../components/TaskCard.vue";
import TaskDetailModal from "../components/TaskDetailModal.vue";
import TaskKanbanBoard from "../components/TaskKanbanBoard.vue";
import TaskLedgerRow from "../components/TaskLedgerRow.vue";
import TaskModal from "../components/TaskModal.vue";
import { showToast } from "../composables/toast";
import { getTaskActivity } from "../services/tasks";
import { useProjectStore } from "../stores/projects";
import { useTaskStore } from "../stores/tasks";
import { withMinLoading } from "../utils/async";
import { exportTasksToCSV, exportTasksToICS, printAcademicLedger } from "../utils/export";

const route = useRoute();
const projectStore = useProjectStore();
const taskStore = useTaskStore();

// View Mode: 'kanban' | 'list' | 'grid'
const viewMode = ref(route.query.view || "kanban");
const localSearch = ref("");
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

// Modals
const isTaskModalOpen = ref(false);
const isEditMode = ref(false);
const selectedTask = ref(null);
const taskModalLoading = ref(false);
const formErrors = ref({});

const isTaskDetailOpen = ref(false);
const detailTaskId = ref(null);

const openDetail = (task) => {
  detailTaskId.value = task.id;
  isTaskDetailOpen.value = true;
};

const isDeleteModalOpen = ref(false);
const taskToDelete = ref(null);
const deleteLoading = ref(false);

// Activity Drawer
const activityTaskId = ref(null);
const activityTaskTitle = ref("");
const activity = ref([]);
const activityLoading = ref(false);
const activityError = ref("");

const error = ref("");

const filters = reactive({
  project_id: route.query.project_id || "",
  status: "",
  priority: "",
  due_from: "",
  due_to: "",
});

const projectName = computed(() => {
  if (!filters.project_id) return "All Courses";
  const p = projectStore.items.find((project) => project.id === Number(filters.project_id));
  return p ? p.name : "All Courses";
});

const hasProjects = computed(() => projectStore.items.length > 0);

const requestMessage = (requestError, fallback) => {
  formErrors.value = requestError.response?.data?.errors || {};
  return requestError.response?.data?.message || fallback;
};

const loadTasks = async () => {
  error.value = "";
  try {
    await withMinLoading(taskStore.fetchTasks(filters), 1800);
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to load tasks.");
  }
};

onMounted(async () => {
  try {
    await projectStore.fetchProjects();
    await loadTasks();

    if (route.query.view) {
      viewMode.value = route.query.view;
    }

    // Auto-open specific task details if queried (e.g. from deep links)
    const targetId = route.query.task_id || route.query.id || route.query.taskId;
    if (targetId) {
      detailTaskId.value = targetId;
      isTaskDetailOpen.value = true;
    }
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to load your task ledger.");
  }
});

const filteredTasks = computed(() => {
  if (!localSearch.value.trim()) return taskStore.items;
  const q = localSearch.value.toLowerCase();
  return taskStore.items.filter(
    (t) => t.title.toLowerCase().includes(q) || (t.description && t.description.toLowerCase().includes(q))
  );
});

const clearFilters = () => {
  Object.assign(filters, { project_id: "", status: "", priority: "", due_from: "", due_to: "" });
  localSearch.value = "";
  loadTasks();
};

const openCreateModal = (defaultStatus = "todo") => {
  isEditMode.value = false;
  selectedTask.value = {
    project_id: filters.project_id || (projectStore.items[0]?.id || ""),
    status: defaultStatus,
  };
  formErrors.value = {};
  isTaskModalOpen.value = true;
};

const openEditModal = (task) => {
  isEditMode.value = true;
  selectedTask.value = task;
  formErrors.value = {};
  isTaskModalOpen.value = true;
};

const toUtcIso = (localInput) => (localInput ? new Date(localInput).toISOString() : null);

const handleSaveTask = async (formData) => {
  taskModalLoading.value = true;
  formErrors.value = {};
  try {
    const payload = {
      ...formData,
      project_id: Number(formData.project_id),
      due_date: toUtcIso(formData.due_date),
    };

    if (isEditMode.value && selectedTask.value) {
      await taskStore.updateTask(selectedTask.value.id, payload);
      showToast("Task updated.");
    } else {
      await taskStore.createTask(payload);
      showToast("Task created.");
    }
    isTaskModalOpen.value = false;
    await loadTasks();
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to save task.");
  } finally {
    taskModalLoading.value = false;
  }
};

const toggleStatus = async (task) => {
  error.value = "";
  try {
    if (task.status === "done") {
      await taskStore.updateTask(task.id, { status: "todo" });
      showToast("Task marked as To Do.");
    } else {
      await taskStore.completeTask(task.id);
      showToast("Task marked as completed.");
    }
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to update task status.");
  }
};

const moveStatus = async (task, newStatus) => {
  error.value = "";
  try {
    if (newStatus === "done") {
      await taskStore.completeTask(task.id);
    } else {
      await taskStore.updateTask(task.id, { status: newStatus });
    }
    showToast(`Task moved to ${newStatus.replace("_", " ")}.`);
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to update status.");
  }
};

const promptDelete = (task) => {
  taskToDelete.value = task;
  isDeleteModalOpen.value = true;
};

const confirmDelete = async () => {
  if (!taskToDelete.value) return;
  deleteLoading.value = true;
  try {
    await taskStore.deleteTask(taskToDelete.value.id);
    if (activityTaskId.value === taskToDelete.value.id) activityTaskId.value = null;
    showToast("Task deleted.");
    isDeleteModalOpen.value = false;
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to delete task.");
  } finally {
    deleteLoading.value = false;
  }
};

const openActivity = async (task) => {
  activityTaskId.value = task.id;
  activityTaskTitle.value = task.title;
  activityLoading.value = true;
  activityError.value = "";
  try {
    const { data } = await getTaskActivity(task.id);
    activity.value = data.activity || [];
  } catch (requestError) {
    activityError.value = requestError.response?.data?.message || "Unable to load task activity.";
  } finally {
    activityLoading.value = false;
  }
};

const activityLabel = (entry) =>
  ({ created: "Created task", updated: "Updated details", status_changed: "Changed status", deleted: "Deleted" }[entry.action] ||
  entry.action.replaceAll("_", " "));

const formatActivityDate = (date) =>
  new Date(date).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
</script>

<template>
  <div class="page-shell">
    <PageHeader
      title="Task Ledger & Workspace"
      :description="projectName === 'All Courses' ? 'Manage your comprehensive academic assignments, deadlines, and project milestones.' : `Filtered for ${projectName}.`"
      :badge="projectName"
    >
      <template #actions>
        <!-- Export Ledger Dropdown with Click-Outside and Animated Transition -->
        <div ref="exportMenuRef" class="relative">
          <button
            class="btn-secondary gap-2"
            type="button"
            :aria-expanded="isExportOpen"
            @click="isExportOpen = !isExportOpen"
          >
            <AppIcon name="sparkles" :size="16" />
            <span>Export Ledger</span>
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
                @click="exportTasksToCSV(filteredTasks, `tasknova-${projectName.toLowerCase().replace(/\s+/g, '-')}-ledger.csv`); isExportOpen = false"
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
                @click="exportTasksToICS(filteredTasks, `TaskNova ${projectName} Deadlines`); isExportOpen = false"
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
                @click="printAcademicLedger(filteredTasks, projectName); isExportOpen = false"
              >
                <span class="flex items-center gap-2.5">
                  <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-300">
                    <AppIcon name="info" :size="15" />
                  </span>
                  <span>Print Assignment Sheet</span>
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
          @click="openCreateModal('todo')"
        >
          <AppIcon name="plus" :size="16" /> Add Task
        </button>
      </template>
    </PageHeader>

    <p v-if="!hasProjects" class="field-help mt-4">
      Create a <router-link class="font-bold text-brand-600 underline dark:text-brand-400" to="/projects">course/project</router-link> before adding tasks.
    </p>

    <!-- Toolbar: Search, View Switcher & Filter Controls -->
    <div class="mt-8 flex flex-col gap-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <!-- Search Input -->
        <div class="relative max-w-md flex-1">
          <AppIcon name="search" :size="16" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            v-model="localSearch"
            type="text"
            class="input-field !mt-0 pl-10"
            placeholder="Quick search tasks..."
          />
        </div>

        <!-- View Mode Switcher -->
        <div class="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white p-1 shadow-sm dark:border-slate-800 dark:bg-night-card">
          <button
            type="button"
            class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold transition-all"
            :class="viewMode === 'kanban' ? 'bg-brand-50 text-brand-700 shadow-sm dark:bg-brand-950/60 dark:text-brand-300' : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'"
            @click="viewMode = 'kanban'"
          >
            <AppIcon name="kanban" :size="14" /> Kanban
          </button>
          <button
            type="button"
            class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold transition-all"
            :class="viewMode === 'list' ? 'bg-brand-50 text-brand-700 shadow-sm dark:bg-brand-950/60 dark:text-brand-300' : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'"
            @click="viewMode = 'list'"
          >
            <AppIcon name="list" :size="14" /> Ledger
          </button>
          <button
            type="button"
            class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold transition-all"
            :class="viewMode === 'grid' ? 'bg-brand-50 text-brand-700 shadow-sm dark:bg-brand-950/60 dark:text-brand-300' : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'"
            @click="viewMode = 'grid'"
          >
            <AppIcon name="grid" :size="14" /> Grid
          </button>
        </div>
      </div>

      <!-- Advanced Filter Form -->
      <form
        class="grid gap-3 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-night-card sm:grid-cols-2 lg:grid-cols-6"
        @submit.prevent="loadTasks"
      >
        <div>
          <label class="field-label">Course / Project</label>
          <select v-model="filters.project_id" class="input-field" @change="loadTasks">
            <option value="">All Courses</option>
            <option v-for="p in projectStore.items" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>

        <div>
          <label class="field-label">Status</label>
          <select v-model="filters.status" class="input-field" @change="loadTasks">
            <option value="">All Statuses</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        </div>

        <div>
          <label class="field-label">Priority</label>
          <select v-model="filters.priority" class="input-field" @change="loadTasks">
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div>
          <label class="field-label">Due From</label>
          <input v-model="filters.due_from" class="input-field" type="date" @change="loadTasks" />
        </div>

        <div>
          <label class="field-label">Due To</label>
          <input v-model="filters.due_to" class="input-field" type="date" @change="loadTasks" />
        </div>

        <div class="flex items-end gap-2">
          <button class="btn-secondary w-full text-xs" type="button" @click="clearFilters">
            Reset
          </button>
          <button class="btn-primary w-full text-xs" type="submit">
            Filter
          </button>
        </div>
      </form>
    </div>

    <!-- Error Alert -->
    <p v-if="error" class="field-error mt-6" aria-live="polite">
      <AppIcon name="alert" :size="16" /> {{ error }}
    </p>

    <!-- Task Content Area -->
    <section class="mt-8">
      <!-- Loading State with UIverse Shimmer Skeleton & AppLoader -->
      <div v-if="taskStore.loading" class="space-y-6">
        <SkeletonLoader :type="viewMode === 'kanban' ? 'board' : (viewMode === 'grid' ? 'cards' : 'rows')" :count="4" />
        <AppLoader size="md" text="Loading academic task ledger" />
      </div>

      <!-- Empty State -->
      <EmptyState
        v-else-if="!filteredTasks.length"
        class="mt-6"
        title="No tasks found matching criteria"
        description="Try adjusting your filters or add a new assignment to keep your ledger moving forward."
      >
        <template #actions>
          <button class="btn-secondary" type="button" @click="clearFilters">Clear All Filters</button>
          <button class="btn-primary" type="button" @click="openCreateModal('todo')">Create Task</button>
        </template>
      </EmptyState>

      <!-- View 1: Kanban Board -->
      <div v-else-if="viewMode === 'kanban'" class="mt-6">
        <TaskKanbanBoard
          :tasks="filteredTasks"
          @toggle-status="toggleStatus"
          @edit="openEditModal"
          @show-activity="openActivity"
          @delete="promptDelete"
          @move-status="moveStatus"
          @add-task-to-status="(status) => openCreateModal(status)"
          @open-detail="openDetail"
        />
      </div>

      <!-- View 2: Ledger List Table -->
      <div v-else-if="viewMode === 'list'" class="mt-6 space-y-3">
        <div class="flex items-center justify-between px-2 text-xs font-bold text-slate-400">
          <span>Displaying {{ filteredTasks.length }} of {{ taskStore.pagination.total }} tasks</span>
        </div>
        <TaskLedgerRow
          v-for="task in filteredTasks"
          :key="task.id"
          :task="task"
          @toggle-status="toggleStatus"
          @edit="openEditModal"
          @show-activity="openActivity"
          @delete="promptDelete"
          @open-detail="openDetail"
        />
      </div>

      <!-- View 3: Grid Cards -->
      <div v-else-if="viewMode === 'grid'" class="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <TaskCard
          v-for="task in filteredTasks"
          :key="task.id"
          :task="task"
          @toggle-status="toggleStatus"
          @edit="openEditModal"
          @show-activity="openActivity"
          @delete="promptDelete"
          @move-status="moveStatus"
          @open-detail="openDetail"
        />
      </div>
    </section>

    <!-- Activity Log Slide-over Drawer -->
    <Teleport to="body">
      <div
        v-if="activityTaskId"
        class="modal-backdrop z-50 animate-fade-in"
      >
        <div class="modal-panel max-w-lg animate-scale-in">
          <div class="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
            <div class="flex items-center gap-2">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-950 dark:text-brand-300">
                <AppIcon name="info" :size="18" />
              </div>
              <div>
                <h3 class="font-display text-sm font-bold text-slate-900 dark:text-white">Audit History</h3>
                <p class="text-[11px] text-slate-400 truncate max-w-[280px]">{{ activityTaskTitle }}</p>
              </div>
            </div>
            <button
              type="button"
              class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
              @click="activityTaskId = null"
            >
              <AppIcon name="x" :size="18" />
            </button>
          </div>

          <div class="my-4 max-h-96 overflow-y-auto pr-1">
            <p v-if="activityLoading" class="py-6 text-center text-xs text-slate-400">Loading audit history...</p>
            <p v-else-if="activityError" class="field-error">{{ activityError }}</p>
            <p v-else-if="!activity.length" class="py-6 text-center text-xs text-slate-400">No recorded changes yet.</p>
            <div v-else class="space-y-2.5">
              <div
                v-for="entry in activity"
                :key="entry.id"
                class="flex items-center justify-between rounded-xl bg-slate-50 p-3 text-xs dark:bg-night-surface"
              >
                <div class="flex items-center gap-2">
                  <span class="h-2 w-2 rounded-full bg-brand-500"></span>
                  <span class="text-slate-700 dark:text-slate-300">
                    <strong class="font-bold text-slate-900 dark:text-white">{{ entry.actor_name }}</strong>
                    {{ activityLabel(entry).toLowerCase() }}
                  </span>
                </div>
                <span class="font-mono text-[11px] text-slate-400">{{ formatActivityDate(entry.created_at) }}</span>
              </div>
            </div>
          </div>

          <div class="border-t border-slate-100 pt-3 text-right dark:border-slate-800">
            <button class="btn-secondary text-xs" type="button" @click="activityTaskId = null">
              Close
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Task Detail Modal -->
    <TaskDetailModal
      :is-open="isTaskDetailOpen"
      :task-id="detailTaskId"
      @close="isTaskDetailOpen = false"
      @edit="openEditModal"
      @delete="promptDelete"
      @updated="loadTasks"
    />

    <!-- Task Create & Edit Modal -->
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

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      :is-open="isDeleteModalOpen"
      title="Delete Task?"
      :message="`Are you sure you want to delete '${taskToDelete?.title}'? This action cannot be reversed.`"
      confirm-text="Delete Task"
      :loading="deleteLoading"
      :is-danger="true"
      @cancel="isDeleteModalOpen = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
