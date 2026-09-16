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
  <div class="surface-card overflow-hidden p-3 transition-all duration-300 sm:p-6">
    <!-- Calendar Toolbar -->
    <div class="flex flex-col gap-3 border-b border-slate-100 pb-3 dark:border-slate-800 sm:gap-4 sm:pb-4 lg:flex-row lg:items-center lg:justify-between">
      <!-- Month & Navigation -->
      <div class="flex min-w-0 items-center gap-2.5 sm:gap-3">
        <div class="flex h-9 w-9 flex-none items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300 sm:h-10 sm:w-10">
          <AppIcon name="calendar" :size="19" />
        </div>
        <div class="min-w-0">
          <h2 class="truncate font-display text-base font-bold text-slate-900 dark:text-white sm:text-lg">
            {{ currentMonthLabel }}
          </h2>
          <p class="truncate text-[11px] text-slate-500 dark:text-slate-400 sm:text-xs">
            {{ filteredTasks.filter(t => t.due_date).length }} scheduled
          </p>
        </div>
      </div>

      <!-- Controls: Today, Prev/Next & Course Filter -->
      <div class="grid grid-cols-[1fr_auto_auto] items-center gap-2 sm:flex sm:flex-wrap">
        <select
          v-model="selectedFilterProject"
          class="input-field min-h-10 !mt-0 w-full min-w-0 truncate text-xs sm:w-auto sm:min-w-[140px]"
        >
          <option value="">All Courses</option>
          <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>

        <button
          type="button"
          class="btn-secondary min-h-10 px-3 text-xs"
          @click="goToToday"
        >
          Today
        </button>

        <div class="flex items-center rounded-xl border border-slate-200 bg-white p-0.5 dark:border-slate-800 dark:bg-night-card">
          <button
            type="button"
            class="min-h-9 min-w-9 rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white"
            title="Previous month"
            aria-label="Previous month"
            @click="prevMonth"
          >
            <AppIcon name="chevron-left" :size="16" />
          </button>
          <button
            type="button"
            class="min-h-9 min-w-9 rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white"
            title="Next month"
            aria-label="Next month"
            @click="nextMonth"
          >
            <AppIcon name="chevron-right" :size="16" />
          </button>
        </div>
      </div>
    </div>

    <!-- Weekday Header Bar -->
    <div class="mt-3 grid grid-cols-7 gap-px rounded-t-xl border border-slate-200/80 bg-slate-100 dark:border-slate-800 dark:bg-night-surface sm:mt-4">
      <div
        v-for="day in weekDays"
        :key="day"
        class="truncate py-1.5 text-center font-mono text-[10px] font-bold text-slate-500 dark:text-slate-400 sm:py-2.5 sm:text-xs"
      >
        <span class="sm:hidden">{{ day.slice(0, 1) }}</span><span class="hidden sm:inline">{{ day }}</span>
      </div>
    </div>

    <!-- Month Grid Container -->
    <div class="grid grid-cols-7 gap-px overflow-hidden rounded-b-xl border-x border-b border-slate-200/80 bg-slate-200/70 dark:border-slate-800 dark:bg-slate-800">
      <div
        v-for="cell in monthGridDays"
        :key="cell.dateKey"
        class="group relative flex min-h-[64px] flex-col bg-white p-1 transition-colors hover:bg-slate-50/80 dark:bg-night-card dark:hover:bg-night-cardHover sm:min-h-[105px] sm:justify-between sm:p-2"
        :class="[
          !cell.isCurrentMonth ? 'opacity-40 bg-slate-50/50 dark:bg-night-surface/50' : '',
          cell.isToday ? 'ring-2 ring-inset ring-brand-500/50 dark:ring-brand-400/50' : ''
        ]"
      >
        <!-- Cell Top: Day Number & Add Action -->
        <div class="flex items-center justify-between">
          <span
            class="flex h-5 w-5 items-center justify-center rounded-full font-mono text-[11px] font-bold sm:h-6 sm:w-6 sm:text-xs"
            :class="cell.isToday
              ? 'bg-brand-600 text-white shadow-sm'
              : (cell.isCurrentMonth ? 'text-slate-800 dark:text-slate-200' : 'text-slate-400 dark:text-slate-600')"
          >
            {{ cell.dayNumber }}
          </span>

          <button
            type="button"
            class="visible rounded p-1 text-slate-400 hover:bg-brand-50 hover:text-brand-600 dark:hover:bg-brand-950 dark:hover:text-brand-300 sm:invisible sm:p-0.5 sm:group-hover:visible"
            title="Add task on this date"
            aria-label="Add task on {{ cell.dateKey }}"
            @click.stop="emit('add-task-on-date', cell.dateKey)"
          >
            <AppIcon name="plus" :size="12" />
          </button>
        </div>

        <!-- Cell Body: Desktop task pills -->
        <div class="my-1.5 hidden max-h-[75px] flex-1 space-y-1 overflow-y-auto pr-0.5 sm:block">
          <div
            v-for="task in cell.tasks"
            :key="task.id"
            class="flex cursor-pointer items-center gap-1 rounded-md border px-1.5 py-0.5 text-[10px] font-semibold transition-transform hover:scale-[1.02]"
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

        <!-- Cell Body: Mobile dots + count -->
        <div class="mt-1 flex min-h-4 flex-1 items-start sm:hidden">
          <button
            v-if="cell.tasks.length"
            type="button"
            class="flex w-full items-center justify-center gap-1 rounded-md py-1"
            @click.stop="emit('open-detail', cell.tasks[0])"
            :aria-label="`${cell.tasks.length} tasks on ${cell.dateKey}`"
          >
            <span class="flex max-w-[36px] items-center gap-0.5 overflow-hidden">
              <span
                v-for="task in cell.tasks.slice(0, 3)"
                :key="task.id"
                class="h-1.5 w-1.5 flex-none rounded-full"
                :class="task.status === 'done' ? 'bg-emerald-500' : (task.priority === 'high' ? 'bg-rose-500' : (task.priority === 'medium' ? 'bg-amber-500' : 'bg-brand-500'))"
              ></span>
            </span>
            <span v-if="cell.tasks.length > 1" class="font-mono text-[9px] font-bold text-slate-500 dark:text-slate-400">+{{ cell.tasks.length }}</span>
          </button>
          <button
            v-else
            type="button"
            class="h-4 w-full rounded-md"
            aria-label="Add task on {{ cell.dateKey }}"
            @click.stop="emit('add-task-on-date', cell.dateKey)"
          ></button>
        </div>

        <!-- Cell Bottom: Tap to Add Area (desktop hover only) -->
        <div
          class="hidden h-3 w-full cursor-pointer text-center text-[10px] text-slate-400 opacity-0 group-hover:opacity-100 sm:block"
          @click="emit('add-task-on-date', cell.dateKey)"
        >
          + Add
        </div>
      </div>
    </div>
  </div>
</template>
