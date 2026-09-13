<script setup>
import { computed, ref } from "vue";
import AppIcon from "./AppIcon.vue";

const props = defineProps({
  tasks: { type: Array, default: () => [] },
  projects: { type: Array, default: () => [] },
});

const emit = defineEmits(["open-detail", "add-task-on-date", "edit"]);

const currentYear = ref(new Date().getFullYear());
const currentMonth = ref(new Date().getMonth()); // 0-indexed
const selectedFilterProject = ref("");
const calendarMode = ref("month"); // 'month' | 'week'

const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const monthNames = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

const currentMonthLabel = computed(() => {
  return `${monthNames[currentMonth.value]} ${currentYear.value}`;
});

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11;
    currentYear.value -= 1;
  } else {
    currentMonth.value -= 1;
  }
};

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0;
    currentYear.value += 1;
  } else {
    currentMonth.value += 1;
  }
};

const goToToday = () => {
  const now = new Date();
  currentYear.value = now.getFullYear();
  currentMonth.value = now.getMonth();
};

const filteredTasks = computed(() => {
  if (!selectedFilterProject.value) return props.tasks;
  return props.tasks.filter((t) => t.project_id === Number(selectedFilterProject.value));
});

// Build map: 'YYYY-MM-DD' -> Task[]
const tasksByDateMap = computed(() => {
  const map = new Map();
  filteredTasks.value.forEach((task) => {
    if (!task.due_date) return;
    const d = new Date(task.due_date);
    const dateKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    if (!map.has(dateKey)) {
      map.set(dateKey, []);
    }
    map.get(dateKey).push(task);
  });
  return map;
});

// Month Calendar Grid Cells calculation
const monthGridDays = computed(() => {
  const year = currentYear.value;
  const month = currentMonth.value;

  const firstDayIndex = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();

  const days = [];
  const today = new Date();
  const todayKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

  // Previous month trailing days
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    const dayNum = daysInPrevMonth - i;
    const prevM = month === 0 ? 11 : month - 1;
    const prevY = month === 0 ? year - 1 : year;
    const dateKey = `${prevY}-${String(prevM + 1).padStart(2, "0")}-${String(dayNum).padStart(2, "0")}`;
    days.push({
      dayNumber: dayNum,
      dateKey,
      isCurrentMonth: false,
      isToday: dateKey === todayKey,
      tasks: tasksByDateMap.value.get(dateKey) || [],
    });
  }

  // Current month days
  for (let d = 1; d <= daysInMonth; d++) {
    const dateKey = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    days.push({
      dayNumber: d,
      dateKey,
      isCurrentMonth: true,
      isToday: dateKey === todayKey,
      tasks: tasksByDateMap.value.get(dateKey) || [],
    });
  }

  // Next month leading days to complete grid (6 rows = 42 cells)
  const remainingCells = 42 - days.length;
  for (let d = 1; d <= remainingCells; d++) {
    const nextM = month === 11 ? 0 : month + 1;
    const nextY = month === 11 ? year + 1 : year;
    const dateKey = `${nextY}-${String(nextM + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    days.push({
      dayNumber: d,
      dateKey,
      isCurrentMonth: false,
      isToday: dateKey === todayKey,
      tasks: tasksByDateMap.value.get(dateKey) || [],
    });
  }

  return days;
});

const getPriorityChipClass = (task) => {
  if (task.status === "done") {
    return "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-900/40 line-through opacity-75";
  }
  const isOverdue = task.due_date && new Date(task.due_date) < new Date();
  if (isOverdue) {
    return "bg-rose-100 text-rose-800 border-rose-300 dark:bg-rose-950/80 dark:text-rose-300 dark:border-rose-800 font-bold animate-pulse";
  }
  if (task.priority === "high") {
    return "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-900/40";
  }
  if (task.priority === "medium") {
    return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-900/40";
  }
  return "bg-brand-50 text-brand-700 border-brand-200 dark:bg-brand-950/40 dark:text-brand-300 dark:border-brand-900/40";
};
</script>

<template>
  <div class="surface-card p-4 sm:p-6 transition-all duration-300">
    <!-- Calendar Toolbar -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-4 dark:border-slate-800">
      <!-- Month & Navigation -->
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300">
          <AppIcon name="calendar" :size="20" />
        </div>
        <div>
          <h2 class="font-display text-lg font-bold text-slate-900 dark:text-white">
            {{ currentMonthLabel }}
          </h2>
          <p class="text-xs text-slate-500 dark:text-slate-400">
            {{ filteredTasks.filter(t => t.due_date).length }} assignments scheduled
          </p>
        </div>
      </div>

      <!-- Controls: Today, Prev/Next & Course Filter -->
      <div class="flex flex-wrap items-center gap-2">
        <select
          v-model="selectedFilterProject"
          class="input-field !mt-0 text-xs min-w-[140px]"
        >
          <option value="">All Courses</option>
          <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>

        <button
          type="button"
          class="btn-secondary text-xs !py-1.5"
          @click="goToToday"
        >
          Today
        </button>

        <div class="flex items-center rounded-xl border border-slate-200 bg-white p-0.5 dark:border-slate-800 dark:bg-night-card">
          <button
            type="button"
            class="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white"
            title="Previous month"
            @click="prevMonth"
          >
            <AppIcon name="chevron-left" :size="16" />
          </button>
          <button
            type="button"
            class="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white"
            title="Next month"
            @click="nextMonth"
          >
            <AppIcon name="chevron-right" :size="16" />
          </button>
        </div>
      </div>
    </div>

    <!-- Weekday Header Bar -->
    <div class="mt-4 grid grid-cols-7 gap-px rounded-t-xl bg-slate-100 dark:bg-night-surface border border-slate-200/80 dark:border-slate-800">
      <div
        v-for="day in weekDays"
        :key="day"
        class="py-2.5 text-center font-mono text-xs font-bold text-slate-500 dark:text-slate-400"
      >
        {{ day }}
      </div>
    </div>

    <!-- Month Grid Container -->
    <div class="grid grid-cols-7 gap-px bg-slate-200/70 dark:bg-slate-800 border-x border-b border-slate-200/80 dark:border-slate-800 rounded-b-xl overflow-hidden">
      <div
        v-for="cell in monthGridDays"
        :key="cell.dateKey"
        class="group relative min-h-[105px] bg-white p-2 transition-colors hover:bg-slate-50/80 dark:bg-night-card dark:hover:bg-night-cardHover flex flex-col justify-between"
        :class="[
          !cell.isCurrentMonth ? 'opacity-40 bg-slate-50/50 dark:bg-night-surface/50' : '',
          cell.isToday ? 'ring-2 ring-inset ring-brand-500/50 dark:ring-brand-400/50' : ''
        ]"
      >
        <!-- Cell Top: Day Number & Add Action -->
        <div class="flex items-center justify-between">
          <span
            class="flex h-6 w-6 items-center justify-center rounded-full font-mono text-xs font-bold"
            :class="cell.isToday
              ? 'bg-brand-600 text-white shadow-sm'
              : (cell.isCurrentMonth ? 'text-slate-800 dark:text-slate-200' : 'text-slate-400 dark:text-slate-600')"
          >
            {{ cell.dayNumber }}
          </span>

          <button
            type="button"
            class="invisible rounded p-0.5 text-slate-400 hover:bg-brand-50 hover:text-brand-600 group-hover:visible dark:hover:bg-brand-950 dark:hover:text-brand-300"
            title="Add task on this date"
            @click.stop="emit('add-task-on-date', cell.dateKey)"
          >
            <AppIcon name="plus" :size="12" />
          </button>
        </div>

        <!-- Cell Body: Task Badges List -->
        <div class="my-1.5 flex-1 space-y-1 overflow-y-auto max-h-[75px] pr-0.5">
          <div
            v-for="task in cell.tasks"
            :key="task.id"
            class="flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[10px] font-semibold cursor-pointer transition-transform hover:scale-[1.02]"
            :class="getPriorityChipClass(task)"
            :title="`${task.title} (${task.project_name || 'No Course'})`"
            @click.stop="emit('open-detail', task)"
          >
            <span
              class="h-1.5 w-1.5 flex-none rounded-full"
              :class="task.status === 'done' ? 'bg-emerald-500' : (task.priority === 'high' ? 'bg-rose-500' : 'bg-brand-500')"
            ></span>
            <span class="truncate">{{ task.title }}</span>
          </div>
        </div>

        <!-- Cell Bottom: Tap to Add Area -->
        <div
          class="h-3 w-full cursor-pointer opacity-0 group-hover:opacity-100 text-[10px] text-slate-400 text-center"
          @click="emit('add-task-on-date', cell.dateKey)"
        >
          + Add
        </div>
      </div>
    </div>
  </div>
</template>
