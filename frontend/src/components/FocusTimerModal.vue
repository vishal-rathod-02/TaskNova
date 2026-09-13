<script setup>
import { computed, ref, watch } from "vue";
import AppIcon from "./AppIcon.vue";
import { useTimerStore } from "../stores/timer";

const props = defineProps({
  isOpen: { type: Boolean, default: false },
});

const emit = defineEmits(["close"]);

const timerStore = useTimerStore();

const modes = [
  { id: "focus", label: "Study Sprint" },
  { id: "shortBreak", label: "Short Break" },
  { id: "longBreak", label: "Long Break" },
];

const tips = [
  "Study in 25-minute sprints without tab switching to maximize memory retention.",
  "Write down quick questions and resolve them right after your timer finishes.",
  "Use short breaks to hydrate, stretch, and give your eyes a rest.",
  "Tackle the highest priority task first before checking messages.",
  "Sprint finishing soon? Stay focused and review your latest sentence.",
];

const randomTip = ref(tips[0]);

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      document.body.style.overflow = "hidden";
      randomTip.value = tips[Math.floor(Math.random() * tips.length)];
    } else {
      document.body.style.overflow = "";
    }
  },
  { immediate: true }
);

const panelUrgencyClass = computed(() => {
  if (timerStore.isUrgent) {
    return "border-rose-400 dark:border-rose-600 shadow-[0_0_40px_rgba(244,63,94,0.35)]";
  }
  if (timerStore.isEndingSoon) {
    return "border-amber-300 dark:border-amber-600 shadow-[0_0_25px_rgba(245,158,11,0.25)]";
  }
  return "border-slate-200 dark:border-slate-700";
});

const digitsColorClass = computed(() => {
  if (timerStore.isUrgent) {
    return "text-rose-600 dark:text-rose-400 drop-shadow-[0_0_16px_rgba(244,63,94,0.6)]";
  }
  if (timerStore.isEndingSoon) {
    return "text-amber-600 dark:text-amber-400 drop-shadow-[0_0_10px_rgba(245,158,11,0.4)]";
  }
  return "text-slate-900 dark:text-white";
});

const progressBarClass = computed(() => {
  if (timerStore.isUrgent) {
    return "from-rose-500 via-amber-500 to-rose-600 shadow-[0_0_12px_rgba(244,63,94,0.6)]";
  }
  if (timerStore.isEndingSoon) {
    return "from-amber-400 to-amber-600 shadow-[0_0_10px_rgba(245,158,11,0.5)]";
  }
  return "from-brand-500 to-indigo-600";
});
</script>

<template>
  <Teleport to="body">
    <!-- Rigid modal backdrop: click does NOT close -->
    <div v-if="isOpen" class="modal-backdrop z-50 animate-fade-in">
      <div
        class="modal-panel max-w-md text-center animate-scale-in transition-all duration-300"
        :class="panelUrgencyClass"
        role="dialog"
        aria-modal="true"
      >
        <!-- Modal Top Header -->
        <div class="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
          <div class="flex items-center gap-2">
            <div
              class="flex h-8 w-8 items-center justify-center rounded-lg transition-colors"
              :class="timerStore.isUrgent
                ? 'bg-rose-100 text-rose-600 dark:bg-rose-950/70 dark:text-rose-300 animate-pulse'
                : (timerStore.isEndingSoon ? 'bg-amber-100 text-amber-600 dark:bg-amber-950/70 dark:text-amber-300' : 'bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300')"
            >
              <AppIcon name="timer" :size="18" />
            </div>
            <div>
              <h3 class="font-display text-base font-bold text-slate-900 dark:text-white">Academic Focus Timer</h3>
            </div>
          </div>
          <button
            type="button"
            class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
            title="Close modal (timer keeps running in background)"
            @click="emit('close')"
          >
            <AppIcon name="x" :size="18" />
          </button>
        </div>

        <!-- Mode selector pills -->
        <div class="mt-5 flex items-center justify-center gap-1.5 rounded-xl bg-slate-100 p-1 dark:bg-night-card">
          <button
            v-for="mode in modes"
            :key="mode.id"
            type="button"
            :class="timerStore.currentMode === mode.id ? 'bg-white text-brand-700 shadow-sm font-bold dark:bg-slate-800 dark:text-white' : 'text-slate-600 dark:text-slate-400'"
            class="flex-1 rounded-lg py-1.5 text-xs font-semibold transition-all"
            @click="timerStore.selectMode(mode.id)"
          >
            {{ mode.label }}
          </button>
        </div>

        <!-- Large Timer Display with Countdown Pulse & Tick-Pop -->
        <div class="relative my-7 flex flex-col items-center justify-center">
          <!-- Urgent Countdown Alert Badge (< 15s / < 10s) -->
          <div
            v-if="timerStore.isUrgent"
            class="mb-3 inline-flex items-center gap-1.5 rounded-full bg-rose-50 border border-rose-200 px-3 py-0.5 text-xs font-bold text-rose-600 dark:bg-rose-950/60 dark:border-rose-900/50 dark:text-rose-300 animate-pulse"
          >
            <span>⚡ Final Sprint! Last {{ timerStore.remainingSeconds }}s</span>
          </div>
          <div
            v-else-if="timerStore.isEndingSoon"
            class="mb-3 inline-flex items-center gap-1.5 rounded-full bg-amber-50 border border-amber-200 px-3 py-0.5 text-xs font-bold text-amber-600 dark:bg-amber-950/60 dark:border-amber-900/50 dark:text-amber-300"
          >
            <span>⏱️ 15s Remaining</span>
          </div>

          <!-- Dynamic Digits with Tick-Pop Micro-Animation -->
          <div
            :key="timerStore.remainingSeconds"
            class="font-mono text-6xl font-extrabold tracking-tight transition-all duration-150"
            :class="[
              digitsColorClass,
              timerStore.isUrgent ? 'animate-tick-pop' : ''
            ]"
          >
            {{ timerStore.formattedTime }}
          </div>

          <span
            class="mt-2 text-xs font-semibold uppercase tracking-wider transition-colors"
            :class="timerStore.isUrgent ? 'text-rose-500 dark:text-rose-400 font-bold' : 'text-slate-400'"
          >
            {{ timerStore.isRunning ? (timerStore.isUrgent ? "Final Sprint Finish!" : "Session in Progress (Active)") : "Paused / Ready" }}
          </span>

          <!-- Animated Progress Bar with Dynamic Gradient -->
          <div class="mt-6 h-2.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <div
              class="h-full rounded-full bg-gradient-to-r transition-all duration-300"
              :class="progressBarClass"
              :style="{ width: `${timerStore.progressPercentage}%` }"
            ></div>
          </div>
        </div>

        <!-- Controls -->
        <div class="flex items-center justify-center gap-3">
          <button
            v-if="!timerStore.isRunning"
            type="button"
            class="btn-primary min-w-28 gap-2"
            @click="timerStore.start()"
          >
            <AppIcon name="play" :size="16" /> Start Focus
          </button>
          <button
            v-else
            type="button"
            class="btn-secondary min-w-28 gap-2"
            :class="timerStore.isUrgent
              ? 'border-rose-300 bg-rose-50 text-rose-700 hover:bg-rose-100 dark:border-rose-800 dark:bg-rose-950/40 dark:text-rose-300'
              : 'border-amber-300 text-amber-700 hover:bg-amber-50 dark:border-amber-700 dark:text-amber-400'"
            @click="timerStore.pause()"
          >
            <AppIcon name="pause" :size="16" /> Pause
          </button>
          <button
            type="button"
            class="btn-secondary"
            @click="timerStore.reset()"
          >
            <AppIcon name="refresh" :size="16" /> Reset
          </button>
        </div>

        <!-- Productivity Note / Urgent Motivation -->
        <div
          class="mt-6 rounded-xl border p-3 text-left text-xs transition-colors"
          :class="timerStore.isUrgent
            ? 'border-rose-200 bg-rose-50/70 text-rose-800 dark:border-rose-900/40 dark:bg-rose-950/30 dark:text-rose-300'
            : 'border-slate-100 bg-slate-50/80 text-slate-500 dark:border-slate-800 dark:bg-night-card dark:text-slate-400'"
        >
          <div class="flex items-center justify-between">
            <div
              class="flex items-center gap-1.5 font-semibold"
              :class="timerStore.isUrgent ? 'text-rose-700 dark:text-rose-300' : 'text-slate-700 dark:text-slate-300'"
            >
              <AppIcon :name="timerStore.isUrgent ? 'fire' : 'sparkles'" :size="14" :class="timerStore.isUrgent ? 'text-rose-500 animate-pulse' : 'text-amber-500'" />
              {{ timerStore.isUrgent ? 'Final Sprint Push:' : 'Study Tip:' }}
            </div>
            <span v-if="timerStore.sessionsCompleted > 0" class="font-mono text-[11px] font-bold text-emerald-600">
              ✓ {{ timerStore.sessionsCompleted }} session{{ timerStore.sessionsCompleted === 1 ? '' : 's' }} completed
            </span>
          </div>
          <p class="mt-1 leading-relaxed">
            {{ timerStore.isUrgent ? 'Almost at the finish line! Hold your attention until the completion chime.' : randomTip }}
          </p>
        </div>

        <!-- Bottom Close Action -->
        <div class="mt-5 border-t border-slate-100 pt-3 text-right dark:border-slate-800">
          <button
            type="button"
            class="btn-secondary text-xs"
            @click="emit('close')"
          >
            Close Dialog
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
