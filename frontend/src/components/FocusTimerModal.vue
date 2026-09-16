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
    <div v-if="isOpen" class="modal-backdrop z-50 animate-fade-in overflow-y-auto">
      <div
        class="modal-panel my-auto flex max-h-[92vh] w-full max-w-md animate-scale-in flex-col overflow-hidden p-4 text-center transition-all duration-300 sm:p-6"
        :class="panelUrgencyClass"
        role="dialog"
        aria-modal="true"
      >
        <!-- Modal Top Header -->
        <div class="flex flex-none items-center justify-between gap-3 border-b border-slate-100 pb-3 dark:border-slate-800">
          <div class="flex min-w-0 flex-1 items-center gap-2">
            <div
              class="flex h-8 w-8 flex-none items-center justify-center rounded-lg transition-colors"
              :class="timerStore.isUrgent
                ? 'bg-rose-100 text-rose-600 dark:bg-rose-950/70 dark:text-rose-300 animate-pulse'
                : (timerStore.isEndingSoon ? 'bg-amber-100 text-amber-600 dark:bg-amber-950/70 dark:text-amber-300' : 'bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300')"
            >
              <AppIcon name="timer" :size="17" />
            </div>
            <h3 class="min-w-0 flex-1 truncate text-left font-display text-sm font-bold text-slate-900 dark:text-white sm:text-base">Academic Focus Timer</h3>
          </div>
          <button
            type="button"
            class="flex min-h-9 min-w-9 flex-none items-center justify-center rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
            title="Close modal (timer keeps running in background)"
            aria-label="Close timer dialog"
            @click="emit('close')"
          >
            <AppIcon name="x" :size="18" />
          </button>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto">

        <!-- Mode selector pills -->
        <div class="mt-4 flex items-center justify-center gap-1 rounded-xl bg-slate-100 p-1 dark:bg-night-card sm:mt-5 sm:gap-1.5">
          <button
            v-for="mode in modes"
            :key="mode.id"
            type="button"
            :class="timerStore.currentMode === mode.id ? 'bg-white text-brand-700 shadow-sm font-bold dark:bg-slate-800 dark:text-white' : 'text-slate-600 dark:text-slate-400'"
            class="min-h-9 flex-1 truncate rounded-lg px-1 py-1.5 text-[11px] font-semibold transition-all sm:text-xs"
            @click="timerStore.selectMode(mode.id)"
          >
            {{ mode.label }}
          </button>
        </div>

        <!-- Large Timer Display with Countdown Pulse & Tick-Pop -->
        <div class="relative my-5 flex flex-col items-center justify-center sm:my-7">
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
            class="font-mono text-5xl font-extrabold tracking-tight transition-all duration-150 sm:text-6xl"
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

        <!-- Sound controls -->
        <div class="mt-5 flex flex-col gap-2 rounded-xl border border-slate-100 bg-slate-50/70 p-3 text-left dark:border-slate-800 dark:bg-night-card/60 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex min-w-0 items-center gap-2">
            <button
              type="button"
              class="flex min-h-9 min-w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 transition-all hover:bg-slate-100 dark:border-slate-700 dark:bg-night-surface dark:text-slate-300"
              :title="timerStore.soundEnabled ? 'Mute timer sounds' : 'Unmute timer sounds'"
              :aria-pressed="timerStore.soundEnabled"
              @click="timerStore.toggleSound()"
            >
              <AppIcon :name="timerStore.soundEnabled ? 'bell' : 'x'" :size="15" />
            </button>
            <div class="min-w-0">
              <p class="truncate text-xs font-bold text-slate-700 dark:text-slate-200">
                {{ timerStore.soundEnabled ? "End sounds on" : "Muted" }}
              </p>
              <p class="truncate text-[11px] text-slate-500 dark:text-slate-400">
                Warn once + ticks 10s + chime
              </p>
            </div>
          </div>
          <label class="flex flex-none items-center gap-2 text-[11px] font-semibold text-slate-600 dark:text-slate-300">
            <span class="whitespace-nowrap">Warn at</span>
            <select
              :value="timerStore.warningThreshold"
              :disabled="!timerStore.soundEnabled"
              class="min-h-9 rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-xs font-bold text-slate-700 disabled:opacity-50 dark:border-slate-700 dark:bg-night-surface dark:text-slate-200"
              @change="timerStore.setWarningThreshold($event.target.value)"
            >
              <option :value="15">15s</option>
              <option :value="30">30s</option>
              <option :value="60">60s</option>
              <option :value="120">2m</option>
            </select>
          </label>
        </div>

        <!-- Controls -->
        <div class="mt-4 flex flex-col-reverse gap-2 sm:flex-row sm:items-center sm:justify-center sm:gap-3">
          <button
            v-if="!timerStore.isRunning"
            type="button"
            class="btn-primary min-h-11 w-full justify-center gap-2 sm:w-auto sm:min-w-28"
            @click="timerStore.start()"
          >
            <AppIcon name="play" :size="16" class="flex-none" /> Start Focus
          </button>
          <button
            v-else
            type="button"
            class="btn-secondary min-h-11 w-full justify-center gap-2 sm:w-auto sm:min-w-28"
            :class="timerStore.isUrgent
              ? 'border-rose-300 bg-rose-50 text-rose-700 hover:bg-rose-100 dark:border-rose-800 dark:bg-rose-950/40 dark:text-rose-300'
              : 'border-amber-300 text-amber-700 hover:bg-amber-50 dark:border-amber-700 dark:text-amber-400'"
            @click="timerStore.pause()"
          >
            <AppIcon name="pause" :size="16" class="flex-none" /> Pause
          </button>
          <button
            type="button"
            class="btn-secondary min-h-11 w-full justify-center sm:w-auto"
            @click="timerStore.reset()"
          >
            <AppIcon name="refresh" :size="16" class="flex-none" /> Reset
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
        </div>

        <!-- Bottom Close Action -->
        <div class="mt-4 flex-none border-t border-slate-100 pt-3 dark:border-slate-800 sm:text-right">
          <button
            type="button"
            class="btn-secondary min-h-11 w-full justify-center text-xs sm:w-auto"
            @click="emit('close')"
          >
            Close Dialog
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
