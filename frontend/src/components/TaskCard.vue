<script setup>
import { computed } from "vue";
import AppIcon from "./AppIcon.vue";
import { parseSubtasks } from "../utils/subtasks";

const props = defineProps({
  task: { type: Object, required: true },
});

const emit = defineEmits(["toggle-status", "edit", "show-activity", "delete", "move-status", "open-detail"]);

const subtaskData = computed(() => parseSubtasks(props.task.description));

const isOverdue = computed(() => {
  return props.task.status !== "done" && props.task.due_date && new Date(props.task.due_date) < new Date();
});

const relativeDue = computed(() => {
  if (!props.task.due_date) return null;
  const now = new Date();
  const due = new Date(props.task.due_date);
  const diffMs = due - now;
  const diffHours = Math.round(diffMs / (1000 * 60 * 60));
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));

  if (diffMs < 0) {
    const overdueDays = Math.abs(diffDays);
    if (overdueDays === 0) return "Overdue today";
    return `Overdue ${overdueDays}d ago`;
  }
  if (diffHours <= 24 && diffHours > 0) {
    return `Due in ${diffHours}h`;
  }
  if (diffDays === 1) return "Due tomorrow";
  if (diffDays > 1 && diffDays <= 7) return `Due in ${diffDays} days`;
  return due.toLocaleDateString(undefined, { month: "short", day: "numeric" });
});

const priorityStyles = computed(() => {
  switch (props.task.priority) {
    case "high":
      return "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900/40";
    case "medium":
      return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/40";
    case "low":
    default:
      return "bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700";
  }
});
</script>

<template>
  <div
    class="surface-card group relative flex flex-col justify-between border-l-4 p-4 transition-all duration-200 hover:-translate-y-1"
    :class="[
      isOverdue ? 'border-l-rose-500 shadow-[0_0_12px_rgba(244,63,94,0.15)]' :
      task.priority === 'high' ? 'border-l-rose-500' :
      task.priority === 'medium' ? 'border-l-amber-500' : 'border-l-slate-400',
      task.status === 'done' ? 'opacity-75 bg-slate-50/50 dark:bg-night-card/50' : ''
    ]"
  >
    <!-- Top Header & Badges -->
    <div>
      <div class="flex flex-wrap items-center justify-between gap-1.5">
        <span
          v-if="task.project_name"
          class="project-badge truncate max-w-[180px]"
          :title="task.project_name"
        >
          <AppIcon name="academic" :size="12" />
          {{ task.project_name }}
        </span>
        <span
          class="inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-bold uppercase tracking-wider"
          :class="priorityStyles"
        >
          {{ task.priority }}
        </span>
      </div>

      <!-- Task Title (Clickable to open details) -->
      <h3
        class="mt-2.5 cursor-pointer font-sans text-sm font-semibold leading-snug text-slate-900 transition-colors hover:text-brand-600 dark:text-white dark:hover:text-brand-400"
        :class="{ 'line-through text-slate-400 dark:text-slate-500': task.status === 'done' }"
        title="Click to view full task details"
        @click="emit('open-detail', task)"
      >
        {{ task.title }}
      </h3>

      <!-- Description Snippet -->
      <p
        v-if="task.description"
        class="mt-1.5 line-clamp-2 cursor-pointer text-xs leading-relaxed text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
        @click="emit('open-detail', task)"
      >
        {{ task.description }}
      </p>

      <!-- Checkpoints Progress Pill -->
      <div v-if="subtaskData.total > 0" class="mt-2.5 flex items-center gap-2">
        <span class="inline-flex items-center gap-1 rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10px] font-bold text-slate-600 dark:bg-night-surface dark:text-slate-300">
          ✓ {{ subtaskData.completed }}/{{ subtaskData.total }}
        </span>
        <div class="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
          <div
            class="h-full rounded-full transition-all duration-300"
            :class="subtaskData.percentage === 100 ? 'bg-emerald-500' : 'bg-brand-500'"
            :style="{ width: `${subtaskData.percentage}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Bottom Meta & Actions -->
    <div class="mt-4 border-t border-slate-100 pt-3 dark:border-slate-800">
      <!-- Due Date Info -->
      <div class="flex items-center justify-between gap-2 text-xs">
        <div
          v-if="relativeDue"
          :class="isOverdue ? 'font-bold text-rose-600 dark:text-rose-400' : 'text-slate-500 dark:text-slate-400'"
          class="flex items-center gap-1"
        >
          <AppIcon name="clock" :size="14" :class="isOverdue ? 'animate-pulse' : ''" />
          <span>{{ relativeDue }}</span>
        </div>
        <div v-else class="text-xs text-slate-400">
          No deadline
        </div>

        <!-- Quick Status Switcher Dropdown / Action -->
        <div class="flex items-center gap-1 opacity-80 group-hover:opacity-100">
          <button
            type="button"
            class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
            title="Open Task Details"
            @click="emit('open-detail', task)"
          >
            <AppIcon name="tasks" :size="14" />
          </button>
          <button
            type="button"
            class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
            title="View Activity History"
            @click="emit('show-activity', task)"
          >
            <AppIcon name="info" :size="14" />
          </button>
          <button
            type="button"
            class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
            title="Edit Task"
            @click="emit('edit', task)"
          >
            <AppIcon name="edit" :size="14" />
          </button>
          <button
            type="button"
            class="rounded-lg p-1 text-rose-400 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/40"
            title="Delete Task"
            @click="emit('delete', task)"
          >
            <AppIcon name="trash" :size="14" />
          </button>
        </div>
      </div>

      <!-- Quick Move Button for Kanban Columns -->
      <div class="mt-3 flex items-center justify-between gap-2">
        <label class="flex cursor-pointer items-center gap-2 text-xs font-semibold text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            :checked="task.status === 'done'"
            class="h-4 w-4 rounded accent-emerald-600 transition-transform active:scale-90"
            @change="emit('toggle-status', task)"
          />
          <span>{{ task.status === 'done' ? 'Completed' : 'Mark Done' }}</span>
        </label>

        <div v-if="task.status !== 'done'" class="flex gap-1">
          <button
            v-if="task.status === 'todo'"
            type="button"
            class="rounded-md bg-amber-50 px-2 py-0.5 text-[11px] font-semibold text-amber-700 hover:bg-amber-100 dark:bg-amber-950/40 dark:text-amber-300"
            @click="emit('move-status', task, 'in_progress')"
          >
            Start &rarr;
          </button>
          <button
            v-else-if="task.status === 'in_progress'"
            type="button"
            class="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300"
            @click="emit('move-status', task, 'todo')"
          >
            &larr; To Do
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
