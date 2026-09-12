<script setup>
import { computed } from "vue";
import AppIcon from "./AppIcon.vue";

const props = defineProps({
  task: { type: Object, required: true },
  showProject: { type: Boolean, default: true },
});

defineEmits(["toggle-status", "edit", "show-activity", "delete"]);

const statusLabel = computed(() => ({ todo: "To do", in_progress: "In progress", done: "Done" }[props.task.status] || props.task.status));
const isOverdue = computed(() => props.task.status !== "done" && props.task.due_date && new Date(props.task.due_date) < new Date());
const priorityTab = computed(() => (isOverdue.value ? "priority-overdue" : `priority-${props.task.priority}`));
const statusClass = computed(() => {
  if (isOverdue.value) return "status-overdue";
  if (props.task.status === "done") return "status-done";
  if (props.task.status === "in_progress") return "status-progress";
  return "";
});
const dueDateLabel = computed(() => {
  if (!props.task.due_date) return "No due date";
  const due = new Date(props.task.due_date);
  if (isOverdue.value) return `Overdue ${due.toLocaleDateString(undefined, { month: "short", day: "numeric" })}`;
  return `Due ${due.toLocaleDateString(undefined, { month: "short", day: "numeric" })}`;
});
</script>

<template>
  <article class="ledger-row" :class="{ 'opacity-70': task.status === 'done' }">
    <span class="priority-tab" :class="priorityTab" aria-hidden="true"></span>
    <div class="min-w-0">
      <div class="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <h3 class="truncate text-base font-medium text-ink dark:text-[#E7E9ED]">{{ task.title }}</h3>
        <span v-if="showProject && task.project_name" class="data-label">{{ task.project_name }}</span>
      </div>
      <p v-if="task.description" class="mt-1 max-w-[72ch] truncate text-sm leading-5 text-slate dark:text-[#9AA3B2]">{{ task.description }}</p>
      <div class="mt-2 flex flex-wrap gap-x-4 gap-y-1">
        <span class="status-chip" :class="statusClass"><span class="status-dot"></span>{{ statusLabel }}</span>
        <span class="status-chip" :class="{ 'text-ember dark:text-ember-dark': isOverdue }"><AppIcon name="clock" :size="16" />{{ dueDateLabel }}</span>
        <span class="status-chip">{{ task.priority }} priority</span>
      </div>
    </div>
    <div class="flex flex-wrap items-center gap-x-3 gap-y-1 sm:justify-end">
      <button class="min-h-11 px-1 text-sm font-medium text-ink underline decoration-slate/50 underline-offset-4 hover:decoration-ink dark:text-[#E7E9ED]" type="button" @click="$emit('show-activity', task)">Activity</button>
      <button class="min-h-11 px-1 text-sm font-medium text-ink underline decoration-slate/50 underline-offset-4 hover:decoration-ink dark:text-[#E7E9ED]" type="button" @click="$emit('edit', task)">Edit</button>
      <button class="min-h-11 px-1 text-sm font-medium text-ember hover:underline dark:text-ember-dark" type="button" @click="$emit('delete', task)">Delete</button>
      <label class="flex min-h-11 cursor-pointer items-center gap-2 text-sm font-medium text-ink dark:text-[#E7E9ED]">
        <input
          :checked="task.status === 'done'"
          class="h-5 w-5 accent-ledger-green"
          type="checkbox"
          :aria-label="`${task.status === 'done' ? 'Reopen' : 'Mark done'} ${task.title}`"
          @change="$emit('toggle-status', task)"
        />
        <span>{{ task.status === "done" ? "Reopen" : "Mark done" }}</span>
      </label>
    </div>
  </article>
</template>
