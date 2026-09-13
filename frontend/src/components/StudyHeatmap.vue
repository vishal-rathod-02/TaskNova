<script setup>
import { computed, ref } from "vue";
import AppIcon from "./AppIcon.vue";

const props = defineProps({
  tasks: { type: Array, default: () => [] },
  stats: { type: Object, default: () => ({}) },
});

const selectedDay = ref(null);

const weekDayLabels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

// Build 12 calendar weeks (columns) strictly Sunday to Saturday
const weekColumns = computed(() => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Map: 'YYYY-MM-DD' -> Task[]
  const dateTasksMap = new Map();

  props.tasks.forEach((task) => {
    if (task.status === "done" && task.updated_at) {
      const d = new Date(task.updated_at);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
      if (!dateTasksMap.has(key)) {
        dateTasksMap.set(key, []);
      }
      dateTasksMap.get(key).push(task);
    }
  });

  // Also include counts from completion_trend stats if present
  const trendCounts = new Map();
  if (props.stats?.completion_trend) {
    props.stats.completion_trend.forEach((item) => {
      trendCounts.set(item.date, item.count);
    });
  }

  // Calculate Sunday of current week
  const todayDayOfWeek = today.getDay(); // 0 = Sun, 1 = Mon, ..., 6 = Sat
  const currentWeekSunday = new Date(today);
  currentWeekSunday.setDate(today.getDate() - todayDayOfWeek);

  // 12 weeks total: start 11 weeks before current week's Sunday
  const startSunday = new Date(currentWeekSunday);
  startSunday.setDate(startSunday.getDate() - (11 * 7));

  const columns = [];
  let lastMonthIndex = -1;

  for (let w = 0; w < 12; w++) {
    const days = [];
    for (let r = 0; r < 7; r++) {
      const d = new Date(startSunday);
      d.setDate(startSunday.getDate() + (w * 7) + r);
      d.setHours(0, 0, 0, 0);

      const dateKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
      const isFuture = d.getTime() > today.getTime();
      const isToday = d.getTime() === today.getTime();
      const dayTasks = isFuture ? [] : (dateTasksMap.get(dateKey) || []);
      const count = isFuture ? 0 : Math.max(dayTasks.length, trendCounts.get(dateKey) || 0);

      days.push({
        date: dateKey,
        dayOfWeek: r,
        dayName: weekDayLabels[r],
        monthName: d.toLocaleDateString(undefined, { month: "short" }),
        monthIndex: d.getMonth(),
        dayOfMonth: d.getDate(),
        year: d.getFullYear(),
        formatted: d.toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric", year: "numeric" }),
        shortFormatted: d.toLocaleDateString(undefined, { month: "short", day: "numeric" }),
        isToday,
        isFuture,
        tasks: dayTasks,
        count,
        level: isFuture ? 0 : (count >= 5 ? 4 : count >= 3 ? 3 : count >= 2 ? 2 : count >= 1 ? 1 : 0),
      });
    }

    // Determine month label for this week column
    const firstDay = days[0];
    let monthLabel = "";
    if (w === 0 || firstDay.monthIndex !== lastMonthIndex) {
      monthLabel = firstDay.monthName;
      lastMonthIndex = firstDay.monthIndex;
    }

    columns.push({
      weekIndex: w,
      monthLabel,
      days,
    });
  }

  return columns;
});

// Flatten all valid (non-future) days for streak analysis
const allValidDays = computed(() => {
  const list = [];
  weekColumns.value.forEach((col) => {
    col.days.forEach((day) => {
      if (!day.isFuture) list.push(day);
    });
  });
  return list;
});

// Currently selected/inspected day (defaults to today)
const inspectedDay = computed(() => {
  if (selectedDay.value) return selectedDay.value;
  const todayItem = allValidDays.value.find((d) => d.isToday);
  return todayItem || allValidDays.value[allValidDays.value.length - 1] || null;
});

const handleSelectDay = (day) => {
  if (!day || day.isFuture) return;
  selectedDay.value = day;
};

const relativeDayBadge = (day) => {
  if (!day) return "";
  if (day.isToday) return "Today";
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const target = new Date(day.year, day.monthIndex, day.dayOfMonth);
  const diffDays = Math.round((now - target) / (1000 * 60 * 60 * 24));
  if (diffDays === 1) return "Yesterday";
  if (diffDays > 1) return `${diffDays} days ago`;
  return "";
};

// Compute current streak and max streak
const streakInfo = computed(() => {
  let currentStreak = 0;
  let maxStreak = 0;
  let tempStreak = 0;

  const valid = allValidDays.value;

  // Scan backwards from today for current streak
  for (let i = valid.length - 1; i >= 0; i--) {
    if (valid[i].count > 0) {
      currentStreak++;
    } else {
      if (i === valid.length - 1) continue;
      break;
    }
  }

  // Calculate longest streak in window
  valid.forEach((day) => {
    if (day.count > 0) {
      tempStreak++;
      if (tempStreak > maxStreak) maxStreak = tempStreak;
    } else {
      tempStreak = 0;
    }
  });

  const totalInWindow = valid.reduce((acc, d) => acc + d.count, 0);

  return { currentStreak, maxStreak, totalInWindow };
});

const getLevelClass = (level, isFuture) => {
  if (isFuture) {
    return "bg-slate-100/60 dark:bg-slate-900/40 opacity-30 border border-dashed border-slate-200 dark:border-slate-800 cursor-not-allowed";
  }
  switch (level) {
    case 4:
      return "bg-brand-600 dark:bg-brand-500 shadow-[0_0_8px_rgba(99,102,241,0.6)] ring-1 ring-brand-400";
    case 3:
      return "bg-brand-500 dark:bg-brand-600";
    case 2:
      return "bg-brand-300 dark:bg-brand-800";
    case 1:
      return "bg-brand-100 dark:bg-brand-950 border border-brand-200 dark:border-brand-900";
    case 0:
    default:
      return "bg-slate-100 dark:bg-slate-800/80 hover:bg-slate-200 dark:hover:bg-slate-700";
  }
};
</script>

<template>
  <div class="surface-card p-5 transition-all duration-300">
    <!-- Header with Streak Counters -->
    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4 dark:border-slate-800">
      <div>
        <div class="flex items-center gap-2">
          <h2 class="section-title">Academic Momentum & Study Matrix</h2>
          <span class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-bold text-amber-700 dark:bg-amber-950/60 dark:text-amber-300">
            <AppIcon name="fire" :size="14" class="text-amber-500 animate-pulse" />
            {{ streakInfo.currentStreak }} Day Streak
          </span>
        </div>
        <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
          Visual record of daily task velocity and study consistency across the last 12 academic weeks
        </p>
      </div>

      <div class="flex items-center gap-3">
        <div class="text-right">
          <span class="data-label !text-[10px] block">Best Streak</span>
          <span class="font-display text-sm font-extrabold text-slate-900 dark:text-white">
            {{ streakInfo.maxStreak }} Days
          </span>
        </div>
        <div class="h-7 w-px bg-slate-200 dark:bg-slate-800"></div>
        <div class="text-right">
          <span class="data-label !text-[10px] block">Quarter Activity</span>
          <span class="font-display text-sm font-extrabold text-brand-600 dark:text-brand-400">
            {{ streakInfo.totalInWindow }} Actions
          </span>
        </div>
      </div>
    </div>

    <!-- Heatmap Grid Matrix with Mobile Touch Support & Horizontal Scroll -->
    <div class="relative mt-5 overflow-x-auto pb-2 focus:outline-none">
      <div class="inline-flex flex-col min-w-[580px] sm:min-w-full">
        <!-- Month X-Axis Headers -->
        <div class="flex pl-10 gap-2 mb-2 text-[11px] font-semibold text-slate-500 dark:text-slate-400 select-none">
          <div
            v-for="col in weekColumns"
            :key="col.weekIndex"
            class="flex-1 text-left font-mono"
          >
            <span v-if="col.monthLabel" class="inline-block font-bold">{{ col.monthLabel }}</span>
          </div>
        </div>

        <!-- Matrix Body: Weekday Y-Axis Labels (Left) + 12 Week Columns -->
        <div class="flex gap-2">
          <!-- Weekday Y-Axis Column (Strictly Sun..Sat) -->
          <div class="flex flex-col justify-between pr-2 text-[10px] font-mono font-medium text-slate-400 dark:text-slate-500 select-none">
            <span class="h-5 flex items-center">Sun</span>
            <span class="h-5 flex items-center">Mon</span>
            <span class="h-5 flex items-center">Tue</span>
            <span class="h-5 flex items-center">Wed</span>
            <span class="h-5 flex items-center">Thu</span>
            <span class="h-5 flex items-center">Fri</span>
            <span class="h-5 flex items-center">Sat</span>
          </div>

          <!-- 12-Week Columns Grid -->
          <div class="flex gap-2 flex-1 justify-between">
            <div
              v-for="col in weekColumns"
              :key="col.weekIndex"
              class="flex flex-col gap-1.5 flex-1"
            >
              <button
                v-for="day in col.days"
                :key="day.date"
                type="button"
                :disabled="day.isFuture"
                class="relative h-5 w-full rounded-md transition-all duration-150 cursor-pointer touch-manipulation focus:outline-none"
                :class="[
                  getLevelClass(day.level, day.isFuture),
                  !day.isFuture ? 'hover:scale-125 hover:z-20 active:scale-95' : '',
                  inspectedDay?.date === day.date && !day.isFuture ? 'ring-2 ring-brand-500 scale-110 z-10 shadow-md ring-offset-1 dark:ring-offset-night-card' : '',
                  day.isToday ? 'ring-1 ring-amber-400 dark:ring-amber-300' : ''
                ]"
                :aria-label="day.isFuture ? 'Future date' : `${day.formatted}: ${day.count} completed tasks`"
                :title="day.isFuture ? 'Future date' : `${day.formatted}: ${day.count} action${day.count === 1 ? '' : 's'}`"
                @mouseenter="handleSelectDay(day)"
                @click.stop="handleSelectDay(day)"
              >
                <!-- Small dot indicator for Today's cell -->
                <span
                  v-if="day.isToday"
                  class="absolute bottom-0.5 right-0.5 h-1 w-1 rounded-full bg-amber-500 pointer-events-none"
                ></span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Day Inspector Bar -->
    <div
      v-if="inspectedDay"
      class="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-200/80 bg-slate-50/90 p-3.5 text-xs dark:border-slate-800 dark:bg-slate-900/60 transition-all duration-200"
    >
      <div class="flex items-center gap-3">
        <div
          class="h-4 w-4 rounded-md flex-none shadow-sm"
          :class="getLevelClass(inspectedDay.level, false)"
        ></div>
        <div class="flex items-center gap-2">
          <span class="font-display font-bold text-slate-900 dark:text-white text-sm">
            {{ inspectedDay.formatted }}
          </span>
          <span
            v-if="relativeDayBadge(inspectedDay)"
            class="rounded-full px-2 py-0.5 text-[10px] font-bold"
            :class="inspectedDay.isToday ? 'bg-brand-100 text-brand-700 dark:bg-brand-950 dark:text-brand-300' : 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300'"
          >
            {{ relativeDayBadge(inspectedDay) }}
          </span>
        </div>
      </div>

      <!-- Action Count & Completed Task Chips -->
      <div class="flex flex-wrap items-center gap-2">
        <span
          class="font-mono text-xs font-bold"
          :class="inspectedDay.count > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'"
        >
          {{ inspectedDay.count > 0 ? `✓ ${inspectedDay.count} task${inspectedDay.count === 1 ? '' : 's'} completed` : 'No recorded activity' }}
        </span>

        <!-- Task title chips -->
        <div v-if="inspectedDay.tasks && inspectedDay.tasks.length > 0" class="flex flex-wrap items-center gap-1.5 ml-1">
          <span
            v-for="t in inspectedDay.tasks.slice(0, 3)"
            :key="t.id"
            class="inline-block max-w-[150px] truncate rounded-lg bg-white px-2.5 py-1 font-medium text-[11px] text-slate-800 shadow-sm dark:bg-slate-800 dark:text-slate-200 border border-slate-200/80 dark:border-slate-700"
            :title="t.title"
          >
            {{ t.title }}
          </span>
          <span v-if="inspectedDay.tasks.length > 3" class="text-[10px] text-slate-400 font-bold">
            +{{ inspectedDay.tasks.length - 3 }} more
          </span>
        </div>
      </div>
    </div>

    <!-- Heatmap Footer & Intensity Legend -->
    <div class="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-3 text-xs text-slate-400 dark:border-slate-800">
      <span class="font-mono text-[11px]">84 Academic Days · Click or hover any cell to inspect exact date</span>

      <div class="flex items-center gap-1.5 font-mono text-[11px]">
        <span>Less</span>
        <div class="flex items-center gap-1">
          <span class="h-3.5 w-3.5 rounded-sm bg-slate-100 dark:bg-slate-800" title="0 tasks"></span>
          <span class="h-3.5 w-3.5 rounded-sm bg-brand-100 dark:bg-brand-950" title="1 task"></span>
          <span class="h-3.5 w-3.5 rounded-sm bg-brand-300 dark:bg-brand-800" title="2 tasks"></span>
          <span class="h-3.5 w-3.5 rounded-sm bg-brand-500 dark:bg-brand-600" title="3-4 tasks"></span>
          <span class="h-3.5 w-3.5 rounded-sm bg-brand-600 dark:bg-brand-500" title="5+ tasks"></span>
        </div>
        <span>More</span>
      </div>
    </div>
  </div>
</template>

