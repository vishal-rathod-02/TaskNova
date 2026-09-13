<script setup>
import { computed } from "vue";
import AppIcon from "./AppIcon.vue";
import { parseSubtasks } from "../utils/subtasks";

const props = defineProps({
  task: { type: Object, required: true },
  showProject: { type: Boolean, default: true },
});

defineEmits(["toggle-status", "edit", "show-activity", "delete", "open-detail"]);

const subtaskData = computed(() => parseSubtasks(props.task.description));

const isOverdue = computed(() => {
  return props.task.status !== "done" && props.task.due_date && new Date(props.task.due_date) < new Date();
});

const priorityTabClass = computed(() => {
  if (isOverdue.value) return "priority-overdue";
  return `priority-${props.task.priority}`;
});

const statusLabel = computed(() => ({
  todo: "To do",
  in_progress: "In progress",
  done: "Done",
}[props.task.status] || props.task.status));

const statusClass = computed(() => {
  if (isOverdue.value) return "status-overdue";
  if (props.task.status === "done") return "status-done";
  if (props.task.status === "in_progress") return "status-progress";
  return "status-todo";
});

const relativeDue = computed(() => {
  if (!props.task.due_date) return "No due date";
  const now = new Date();
  const due = new Date(props.task.due_date);
  const diffMs = due - now;
  const diffHours = Math.round(diffMs / (1000 * 60 * 60));
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));

  if (diffMs < 0) {
    const overdueDays = Math.abs(diffDays);
    if (overdueDays === 0) return "Overdue today";
    return `Overdue by ${overdueDays}d`;
  }
  if (diffHours <= 24 && diffHours > 0) {
    return `Due in ${diffHours}h`;
  }
  if (diffDays === 1) return "Due tomorrow";
  if (diffDays > 1 && diffDays <= 7) return `Due in ${diffDays} days`;
  return `Due ${due.toLocaleDateString(undefined, { month: "short", day: "numeric" })}`;
});
</script>

<template>
  <article
    class="ledger-row pl-5"
    :class="{ 'opacity-70 bg-slate-50/50 dark:bg-night-card/50': task.status === 'done' }"
  >
    <!-- Priority border tab -->
    <span class="priority-tab" :class="priorityTabClass" aria-hidden="true"></span>

    <!-- Left Content -->
    <div class="min-w-0 flex-1">
      <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
        <h3
          class="cursor-pointer font-sans text-sm font-bold text-slate-900 transition-colors hover:text-brand-600 dark:text-white dark:hover:text-brand-400"
          :class="{ 'line-through text-slate-400 dark:text-slate-500': task.status === 'done' }"
          title="Click to view full task details"
          @click="$emit('open-detail', task)"
        >
          {{ task.title }}
        </h3>
        <span
          v-if="showProject && task.project_name"
          class="project-badge truncate max-w-[200px]"
        >
          <AppIcon name="academic" :size="12" />
          {{ task.project_name }}
        </span>
      </div>

      <p
        v-if="task.description"
        class="mt-1 line-clamp-1 max-w-[72ch] cursor-pointer text-xs text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
        @click="$emit('open-detail', task)"
      >
        {{ task.description }}
      </p>

      <!-- Status, Deadline, Priority & Subtasks Meta -->
      <div class="mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1.5">
        <span class="status-chip" :class="statusClass">
          <span class="status-dot"></span>
          {{ statusLabel }}
        </span>

        <span
          class="inline-flex items-center gap-1 text-xs"
          :class="isOverdue ? 'font-bold text-rose-600 dark:text-rose-400' : 'text-slate-500 dark:text-slate-400'"
        >
          <AppIcon name="clock" :size="14" :class="isOverdue ? 'animate-pulse' : ''" />
          {{ relativeDue }}
        </span>

        <span class="font-mono text-xs capitalize text-slate-400 dark:text-slate-500">
          {{ task.priority }} priority
        </span>

        <!-- Subtasks Checkpoint Indicator -->
        <span
          v-if="subtaskData.total > 0"
          class="inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-0.5 font-mono text-[11px] font-bold text-slate-600 dark:bg-night-surface dark:text-slate-300"
        >
          ✓ {{ subtaskData.completed }}/{{ subtaskData.total }} subtasks
        </span>
      </div>
    </div>

    <!-- Right Controls / Actions -->
    <div class="flex flex-wrap items-center gap-2 border-t border-slate-100 pt-2 sm:border-t-0 sm:pt-0">
      <button
        class="btn-ghost text-brand-600 dark:text-brand-400"
        type="button"
        title="View details"
        @click="$emit('open-detail', task)"
      >
        <AppIcon name="tasks" :size="14" /> Details
      </button>

      <button
        class="btn-ghost"
        type="button"
        title="View activity log"
        @click="$emit('show-activity', task)"
      >
        <AppIcon name="info" :size="14" /> Activity
      </button>

      <button
        class="btn-ghost"
        type="button"
        title="Edit task"
        @click="$emit('edit', task)"
      >
        <AppIcon name="edit" :size="14" /> Edit
      </button>

      <button
        class="btn-ghost text-rose-500 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/40"
        type="button"
        title="Delete task"
        @click="$emit('delete', task)"
      >
        <AppIcon name="trash" :size="14" />
      </button>

      <!-- Complete Checkbox -->
      <label class="ml-1 flex cursor-pointer items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50/80 px-2.5 py-1 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:bg-night-surface dark:text-slate-200 dark:hover:bg-slate-800">
        <input
          :checked="task.status === 'done'"
          class="h-4 w-4 rounded accent-emerald-600 transition-transform active:scale-90"
          type="checkbox"
          :aria-label="`${task.status === 'done' ? 'Reopen' : 'Mark done'} ${task.title}`"
          @change="$emit('toggle-status', task)"
        />
        <span>{{ task.status === "done" ? "Reopen" : "Mark Done" }}</span>
      </label>
    </div>
  </article>
</template>
