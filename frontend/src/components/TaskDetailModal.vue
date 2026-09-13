<script setup>
import { computed, ref, watch } from "vue";
import AcademicNotes from "./AcademicNotes.vue";
import AppIcon from "./AppIcon.vue";
import AppLoader from "./AppLoader.vue";
import { completeTask, getTask, getTaskActivity, updateTask } from "../services/tasks";
import { showToast } from "../composables/toast";
import { withMinLoading } from "../utils/async";
import { addSubtaskToText, toggleSubtaskInText } from "../utils/subtasks";

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  taskId: { type: [Number, String], default: null },
  initialTask: { type: Object, default: () => null },
});

const emit = defineEmits(["close", "edit", "delete", "updated"]);

const task = ref(null);
const loading = ref(false);
const error = ref("");
const activity = ref([]);
const activityLoading = ref(false);
const statusUpdating = ref(false);
const newSubtaskTitle = ref("");
const addingSubtask = ref(false);

const isOverdue = computed(() => {
  return task.value && task.value.status !== "done" && task.value.due_date && new Date(task.value.due_date) < new Date();
});

const statusLabel = computed(() => ({
  todo: "To Do",
  in_progress: "In Progress",
  done: "Completed",
}[task.value?.status] || task.value?.status));

const relativeDue = computed(() => {
  if (!task.value?.due_date) return "No deadline set";
  const now = new Date();
  const due = new Date(task.value.due_date);
  const diffMs = due - now;
  const diffHours = Math.round(diffMs / (1000 * 60 * 60));
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));

  if (diffMs < 0) {
    const overdueDays = Math.abs(diffDays);
    if (overdueDays === 0) return "Overdue today";
    return `Overdue by ${overdueDays} day${overdueDays === 1 ? '' : 's'}`;
  }
  if (diffHours <= 24 && diffHours > 0) return `Due in ${diffHours} hour${diffHours === 1 ? '' : 's'}`;
  if (diffDays === 1) return "Due tomorrow";
  if (diffDays > 1 && diffDays <= 7) return `Due in ${diffDays} days`;
  return `Due ${due.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })}`;
});

const priorityStyles = computed(() => {
  switch (task.value?.priority) {
    case "high":
      return "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900/40";
    case "medium":
      return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/40";
    case "low":
    default:
      return "bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700";
  }
});

const loadDetails = async () => {
  if (!props.taskId) return;
  loading.value = true;
  error.value = "";
  activityLoading.value = true;

  try {
    const [taskRes, actRes] = await withMinLoading(
      Promise.all([
        getTask(props.taskId),
        getTaskActivity(props.taskId).catch(() => ({ data: { activity: [] } })),
      ]),
      600
    );

    task.value = taskRes.data.task;
    activity.value = actRes.data?.activity || [];
  } catch (err) {
    error.value = err.response?.data?.message || "Unable to load task details.";
  } finally {
    loading.value = false;
    activityLoading.value = false;
  }
};

watch(
  () => [props.isOpen, props.taskId],
  ([open, id]) => {
    if (open) {
      document.body.style.overflow = "hidden";
      if (props.initialTask) {
        task.value = props.initialTask;
      }
      if (id) {
        loadDetails();
      }
    } else {
      document.body.style.overflow = "";
      task.value = null;
      activity.value = [];
      newSubtaskTitle.value = "";
    }
  },
  { immediate: true }
);

const handleStatusChange = async (newStatus) => {
  if (!task.value) return;
  statusUpdating.value = true;
  try {
    if (newStatus === "done") {
      const { data } = await completeTask(task.value.id);
      task.value = data.task;
      showToast("Task marked as completed!");
    } else {
      const { data } = await updateTask(task.value.id, { status: newStatus });
      task.value = data.task;
      showToast(`Task moved to ${newStatus.replace("_", " ")}.`);
    }
    emit("updated", task.value);
    // Refresh activity log
    const actRes = await getTaskActivity(task.value.id).catch(() => ({ data: { activity: [] } }));
    activity.value = actRes.data?.activity || [];
  } catch (err) {
    showToast(err.response?.data?.message || "Unable to update status.", "error");
  } finally {
    statusUpdating.value = false;
  }
};

const handleToggleSubtask = async (subtaskIdx) => {
  if (!task.value) return;
  const updatedDesc = toggleSubtaskInText(task.value.description, subtaskIdx);
  task.value.description = updatedDesc;

  try {
    await updateTask(task.value.id, { description: updatedDesc });
    emit("updated", task.value);
  } catch (err) {
    showToast("Unable to update checkpoint status.", "error");
  }
};

const handleAddSubtask = async () => {
  if (!task.value || !newSubtaskTitle.value.trim()) return;
  addingSubtask.value = true;
  const updatedDesc = addSubtaskToText(task.value.description, newSubtaskTitle.value);
  task.value.description = updatedDesc;
  newSubtaskTitle.value = "";

  try {
    await updateTask(task.value.id, { description: updatedDesc });
    showToast("Checkpoint added to syllabus.");
    emit("updated", task.value);
  } catch (err) {
    showToast("Unable to add subtask.", "error");
  } finally {
    addingSubtask.value = false;
  }
};

const activityLabel = (entry) =>
  ({ created: "Created task", updated: "Updated details", status_changed: "Changed status", deleted: "Deleted" }[entry.action] ||
  entry.action.replaceAll("_", " "));

const formatActivityDate = (date) =>
  new Date(date).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
</script>

<template>
  <Teleport to="body">
    <!-- Rigid Backdrop: Click outside does NOT close -->
    <div v-if="isOpen" class="modal-backdrop z-50 animate-fade-in">
      <div class="modal-panel max-w-2xl animate-scale-in" role="dialog" aria-modal="true">
        <!-- Top Header -->
        <div class="flex items-start justify-between border-b border-slate-100 pb-4 dark:border-slate-800">
          <div class="flex items-center gap-3">
            <div class="flex h-11 w-11 flex-none items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300">
              <AppIcon name="tasks" :size="22" />
            </div>
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <span class="data-label">Task Details & Record</span>
                <span v-if="task?.project_name" class="project-badge">
                  <AppIcon name="academic" :size="12" /> {{ task.project_name }}
                </span>
              </div>
              <h2 class="font-display text-lg font-bold text-slate-900 dark:text-white">
                {{ task?.title || 'Academic Task' }}
              </h2>
            </div>
          </div>
          <button
            type="button"
            class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
            title="Close dialog"
            @click="emit('close')"
          >
            <AppIcon name="x" :size="20" />
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="loading && !task" class="py-12">
          <AppLoader size="md" text="Loading task details & audit history" />
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="py-8 text-center">
          <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-50 text-rose-600 dark:bg-rose-950 dark:text-rose-400">
            <AppIcon name="alert" :size="24" />
          </div>
          <p class="mt-3 text-xs font-semibold text-rose-600 dark:text-rose-400">{{ error }}</p>
          <button class="btn-secondary mt-4 text-xs" type="button" @click="loadDetails">
            <AppIcon name="refresh" :size="14" /> Retry
          </button>
        </div>

        <!-- Main Task Content -->
        <div v-else-if="task" class="my-5 max-h-[70vh] space-y-5 overflow-y-auto pr-1">
          <!-- Status, Priority, and Deadline Badges Bar -->
          <div class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-100 bg-slate-50/70 p-3.5 dark:border-slate-800 dark:bg-night-card">
            <!-- Left Meta -->
            <div class="flex flex-wrap items-center gap-2.5">
              <!-- Priority -->
              <span
                class="inline-flex items-center gap-1 rounded-md border px-2.5 py-1 text-xs font-bold uppercase tracking-wider"
                :class="priorityStyles"
              >
                {{ task.priority }} Priority
              </span>

              <!-- Due date -->
              <span
                class="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-semibold"
                :class="isOverdue
                  ? 'bg-rose-100 text-rose-800 border border-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-900/50'
                  : 'bg-slate-200/70 text-slate-700 dark:bg-slate-800 dark:text-slate-300'"
              >
                <AppIcon name="clock" :size="14" :class="isOverdue ? 'animate-pulse text-rose-600' : ''" />
                {{ relativeDue }}
              </span>
            </div>

            <!-- Right: Interactive Status Pill Switcher -->
            <div class="flex items-center gap-1">
              <button
                type="button"
                :disabled="statusUpdating"
                :class="task.status === 'todo'
                  ? 'bg-brand-600 text-white shadow-sm font-bold'
                  : 'bg-white text-slate-600 hover:bg-slate-100 dark:bg-night-surface dark:text-slate-400 dark:hover:bg-slate-800'"
                class="rounded-lg px-2.5 py-1 text-xs font-semibold transition-all"
                @click="handleStatusChange('todo')"
              >
                To Do
              </button>
              <button
                type="button"
                :disabled="statusUpdating"
                :class="task.status === 'in_progress'
                  ? 'bg-amber-500 text-white shadow-sm font-bold'
                  : 'bg-white text-slate-600 hover:bg-slate-100 dark:bg-night-surface dark:text-slate-400 dark:hover:bg-slate-800'"
                class="rounded-lg px-2.5 py-1 text-xs font-semibold transition-all"
                @click="handleStatusChange('in_progress')"
              >
                In Progress
              </button>
              <button
                type="button"
                :disabled="statusUpdating"
                :class="task.status === 'done'
                  ? 'bg-emerald-600 text-white shadow-sm font-bold'
                  : 'bg-white text-slate-600 hover:bg-slate-100 dark:bg-night-surface dark:text-slate-400 dark:hover:bg-slate-800'"
                class="rounded-lg px-2.5 py-1 text-xs font-semibold transition-all"
                @click="handleStatusChange('done')"
              >
                ✓ Completed
              </button>
            </div>
          </div>

          <!-- Description & Academic Notes Section -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="data-label block">Assignment Notes & Syllabus</span>
            </div>
            
            <div class="rounded-xl border border-slate-100 bg-white p-4 dark:border-slate-800 dark:bg-night-card">
              <AcademicNotes
                v-if="task.description"
                :content="task.description"
                @toggle-subtask="handleToggleSubtask"
              />
              <p v-else class="text-xs italic text-slate-400">
                No description or syllabus details provided yet.
              </p>

              <!-- Quick Add Checkpoint/Subtask Form -->
              <form class="mt-4 flex items-center gap-2 border-t border-slate-100 pt-3 dark:border-slate-800" @submit.prevent="handleAddSubtask">
                <input
                  v-model="newSubtaskTitle"
                  type="text"
                  placeholder="+ Add new checkpoint / subtask item..."
                  class="input-field !mt-0 text-xs py-1.5"
                />
                <button
                  type="submit"
                  class="btn-primary !min-h-8 text-xs px-3"
                  :disabled="!newSubtaskTitle.trim() || addingSubtask"
                >
                  Add
                </button>
              </form>
            </div>
          </div>

          <!-- Audit Activity History Section -->
          <div>
            <div class="flex items-center justify-between">
              <span class="data-label block">Audit History & Timeline</span>
              <span class="font-mono text-[11px] text-slate-400">{{ activity.length }} Events</span>
            </div>

            <div class="mt-2 rounded-xl border border-slate-100 bg-slate-50/50 p-3 dark:border-slate-800 dark:bg-night-surface">
              <p v-if="activityLoading" class="py-3 text-center text-xs text-slate-400">Loading audit events...</p>
              <p v-else-if="!activity.length" class="py-3 text-center text-xs text-slate-400">No recorded changes yet.</p>
              <div v-else class="space-y-2">
                <div
                  v-for="entry in activity"
                  :key="entry.id"
                  class="flex items-center justify-between rounded-lg bg-white p-2.5 text-xs dark:bg-night-card"
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
          </div>
        </div>

        <!-- Bottom Actions -->
        <div class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4 dark:border-slate-800">
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="btn-ghost"
              @click="emit('edit', task)"
            >
              <AppIcon name="edit" :size="14" /> Edit Task
            </button>
            <button
              type="button"
              class="btn-ghost text-rose-500 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/40"
              @click="emit('delete', task)"
            >
              <AppIcon name="trash" :size="14" /> Delete Task
            </button>
          </div>

          <button
            type="button"
            class="btn-secondary text-xs"
            @click="emit('close')"
          >
            Close Details
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
