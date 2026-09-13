<script setup>
import { computed } from "vue";
import AppIcon from "./AppIcon.vue";
import TaskCard from "./TaskCard.vue";

const props = defineProps({
  tasks: { type: Array, default: () => [] },
});

const emit = defineEmits([
  "toggle-status",
  "edit",
  "show-activity",
  "delete",
  "move-status",
  "add-task-to-status",
  "open-detail",
]);

const todoTasks = computed(() => props.tasks.filter((t) => t.status === "todo"));
const inProgressTasks = computed(() => props.tasks.filter((t) => t.status === "in_progress"));
const doneTasks = computed(() => props.tasks.filter((t) => t.status === "done"));

const columns = computed(() => [
  {
    id: "todo",
    title: "To Do",
    icon: "tasks",
    tasks: todoTasks.value,
    colorClass: "bg-slate-500",
    badgeClass: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
    headerBg: "border-slate-200 bg-slate-50/70 dark:border-slate-800 dark:bg-night-card/50",
  },
  {
    id: "in_progress",
    title: "In Progress",
    icon: "clock",
    tasks: inProgressTasks.value,
    colorClass: "bg-amber-500",
    badgeClass: "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300",
    headerBg: "border-amber-200 bg-amber-50/50 dark:border-amber-900/30 dark:bg-amber-950/20",
  },
  {
    id: "done",
    title: "Done / Completed",
    icon: "check-circle",
    tasks: doneTasks.value,
    colorClass: "bg-emerald-500",
    badgeClass: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300",
    headerBg: "border-emerald-200 bg-emerald-50/50 dark:border-emerald-900/30 dark:bg-emerald-950/20",
  },
]);
</script>

<template>
  <div class="grid gap-6 lg:grid-cols-3">
    <div
      v-for="col in columns"
      :key="col.id"
      class="flex flex-col rounded-2xl border border-slate-200/80 bg-slate-100/40 p-4 dark:border-slate-800 dark:bg-night-surface/50"
    >
      <!-- Column Header -->
      <div
        class="flex items-center justify-between rounded-xl border p-3 shadow-sm"
        :class="col.headerBg"
      >
        <div class="flex items-center gap-2.5">
          <span class="h-2.5 w-2.5 rounded-full" :class="col.colorClass"></span>
          <h3 class="font-display text-sm font-bold text-slate-900 dark:text-white">
            {{ col.title }}
          </h3>
          <span
            class="rounded-full px-2 py-0.5 font-mono text-xs font-bold"
            :class="col.badgeClass"
          >
            {{ col.tasks.length }}
          </span>
        </div>
        <button
          type="button"
          class="flex h-7 w-7 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-white hover:text-brand-600 dark:hover:bg-slate-800 dark:hover:text-brand-400"
          title="Add task in this column"
          @click="emit('add-task-to-status', col.id)"
        >
          <AppIcon name="plus" :size="16" />
        </button>
      </div>

      <!-- Column Tasks Container -->
      <div class="mt-4 flex-1 space-y-3 overflow-y-auto pr-1">
        <div
          v-if="!col.tasks.length"
          class="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 py-10 text-center dark:border-slate-800"
        >
          <p class="text-xs font-medium text-slate-400 dark:text-slate-500">No tasks in this column</p>
          <button
            type="button"
            class="mt-2 text-xs font-semibold text-brand-600 hover:underline dark:text-brand-400"
            @click="emit('add-task-to-status', col.id)"
          >
            + Add one
          </button>
        </div>

        <TaskCard
          v-for="task in col.tasks"
          :key="task.id"
          :task="task"
          @toggle-status="emit('toggle-status', $event)"
          @edit="emit('edit', $event)"
          @show-activity="emit('show-activity', $event)"
          @delete="emit('delete', $event)"
          @move-status="(t, status) => emit('move-status', t, status)"
          @open-detail="emit('open-detail', $event)"
        />
      </div>
    </div>
  </div>
</template>
