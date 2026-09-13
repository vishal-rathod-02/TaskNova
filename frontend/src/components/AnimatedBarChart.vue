<script setup>
import { computed, ref } from "vue";
import AnimatedNumber from "./AnimatedNumber.vue";
import AppIcon from "./AppIcon.vue";

const props = defineProps({
  trend: { type: Array, default: () => [] },
});

const hoveredIndex = ref(null);

const maxCount = computed(() => {
  const counts = props.trend.map((item) => item.count || 0);
  return Math.max(...counts, 1);
});

const totalCompleted = computed(() => {
  return props.trend.reduce((sum, item) => sum + (item.count || 0), 0);
});

const avgPerDay = computed(() => {
  if (!props.trend.length) return 0;
  return (totalCompleted.value / props.trend.length).toFixed(1);
});

const peakDay = computed(() => {
  if (!props.trend.length) return null;
  let max = -1;
  let peak = null;
  props.trend.forEach((item) => {
    if (item.count > max) {
      max = item.count;
      peak = item;
    }
  });
  return max > 0 ? peak : null;
});

const formatWeekday = (dateStr) => {
  if (!dateStr) return "";
  const d = new Date(`${dateStr}T00:00:00`);
  return d.toLocaleDateString(undefined, { weekday: "short" });
};

const formatFullDate = (dateStr) => {
  if (!dateStr) return "";
  const d = new Date(`${dateStr}T00:00:00`);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
};

const getBarHeight = (count) => {
  if (count === 0) return "6%";
  const pct = (count / maxCount.value) * 100;
  return `${Math.max(pct, 12)}%`;
};
</script>

<template>
  <div class="surface-card relative overflow-hidden transition-all duration-300">
    <!-- Chart Header with Summary Stats -->
    <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4 dark:border-slate-800">
      <div>
        <div class="flex items-center gap-2">
          <h2 class="section-title">Weekly Productivity Trend</h2>
          <span class="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            Live
          </span>
        </div>
        <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
          Daily assignment & study task completions over the last 7 days
        </p>
      </div>

      <!-- Quick Metrics Pill -->
      <div class="flex items-center gap-2">
        <div class="rounded-xl border border-slate-100 bg-slate-50/80 px-3 py-1.5 text-right dark:border-slate-800 dark:bg-night-surface">
          <span class="data-label !text-[10px] block">7-Day Total</span>
          <span class="font-display text-sm font-extrabold text-slate-900 dark:text-white">
            <AnimatedNumber :value="totalCompleted" />
          </span>
        </div>

        <div class="rounded-xl border border-slate-100 bg-slate-50/80 px-3 py-1.5 text-right dark:border-slate-800 dark:bg-night-surface">
          <span class="data-label !text-[10px] block">Daily Avg</span>
          <span class="font-display text-sm font-extrabold text-brand-600 dark:text-brand-400">
            {{ avgPerDay }}
          </span>
        </div>
      </div>
    </div>

    <!-- Interactive Bar Chart Stage -->
    <div class="relative mt-8">
      <!-- Background Grid lines -->
      <div class="pointer-events-none absolute inset-0 flex flex-col justify-between opacity-15 dark:opacity-10">
        <div class="w-full border-b border-dashed border-slate-400"></div>
        <div class="w-full border-b border-dashed border-slate-400"></div>
        <div class="w-full border-b border-dashed border-slate-400"></div>
      </div>

      <!-- Bars Container -->
      <div class="relative flex h-52 items-end justify-between gap-2.5 sm:gap-4 px-2 pb-2">
        <div
          v-for="(item, index) in trend"
          :key="item.date"
          class="group relative flex h-full min-w-0 flex-1 flex-col justify-end items-center cursor-pointer"
          @mouseenter="hoveredIndex = index"
          @mouseleave="hoveredIndex = null"
        >
          <!-- Floating Interactive Glass Tooltip on Hover -->
          <div
            class="pointer-events-none absolute -top-14 z-20 flex flex-col items-center rounded-xl border border-slate-200/80 bg-slate-900/95 px-3 py-1.5 text-white shadow-xl backdrop-blur-md transition-all duration-200 dark:border-slate-700 dark:bg-night-surface/95"
            :class="hoveredIndex === index ? 'opacity-100 scale-100 -translate-y-1' : 'opacity-0 scale-95 pointer-events-none'"
          >
            <span class="font-mono text-[10px] font-semibold text-brand-300">
              {{ formatFullDate(item.date) }}
            </span>
            <span class="font-display text-xs font-bold text-white whitespace-nowrap">
              {{ item.count }} task{{ item.count === 1 ? '' : 's' }} completed
            </span>
            <div class="absolute -bottom-1 h-2 w-2 rotate-45 bg-slate-900 dark:bg-night-surface"></div>
          </div>

          <!-- Number Indicator on top of bar with rollup animation -->
          <div class="mb-2 transition-transform duration-200 group-hover:-translate-y-1">
            <span
              class="inline-flex items-center justify-center rounded-md px-1.5 py-0.5 font-mono text-xs font-bold transition-colors"
              :class="[
                item.count > 0 ? 'text-slate-700 dark:text-slate-200' : 'text-slate-400 dark:text-slate-600',
                hoveredIndex === index ? 'bg-brand-100 text-brand-800 dark:bg-brand-950 dark:text-brand-300 shadow-sm' : ''
              ]"
            >
              <AnimatedNumber :value="item.count" :duration="700 + index * 50" />
            </span>
          </div>

          <!-- Animated Dynamic Bar with Sheen & Glow -->
          <div class="relative w-full max-w-[48px] flex items-end justify-center h-full">
            <div
              class="w-full rounded-t-xl transition-all duration-500 ease-out group-hover:shadow-glow-md"
              :class="[
                item.count > 0
                  ? 'bg-gradient-to-t from-brand-600 via-brand-500 to-indigo-400 group-hover:from-brand-500 group-hover:to-cyan-400'
                  : 'bg-slate-200/60 dark:bg-slate-800/60 border border-dashed border-slate-300 dark:border-slate-700',
                hoveredIndex === index ? 'scale-x-105 brightness-110' : ''
              ]"
              :style="{
                height: getBarHeight(item.count),
                animation: `barRise 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards ${index * 70}ms`,
              }"
            >
              <!-- Luminous Sheen line on top edge of active bar -->
              <div
                v-if="item.count > 0"
                class="h-1 w-full rounded-t-xl bg-white/50 dark:bg-cyan-200/60"
              ></div>
            </div>
          </div>

          <!-- Weekday & Date Label below -->
          <div class="mt-3 flex flex-col items-center">
            <span
              class="font-display text-xs font-bold transition-colors"
              :class="hoveredIndex === index ? 'text-brand-600 dark:text-brand-400' : 'text-slate-600 dark:text-slate-300'"
            >
              {{ formatWeekday(item.date) }}
            </span>
            <span class="font-mono text-[10px] text-slate-400 dark:text-slate-500">
              {{ new Date(`${item.date}T00:00:00`).getDate() }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Peak Momentum Footnote -->
    <div
      v-if="peakDay"
      class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400"
    >
      <div class="flex items-center gap-1.5">
        <AppIcon name="fire" :size="14" class="text-amber-500 animate-pulse" />
        <span>
          Peak velocity on <strong class="font-semibold text-slate-800 dark:text-slate-200">{{ formatWeekday(peakDay.date) }}, {{ formatFullDate(peakDay.date) }}</strong> ({{ peakDay.count }} completions)
        </span>
      </div>
      <span class="font-mono text-[11px] text-slate-400">
        Consistency Score: <strong class="text-emerald-600 dark:text-emerald-400 font-bold">Optimal</strong>
      </span>
    </div>
  </div>
</template>
