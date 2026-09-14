<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRouter } from "vue-router";
import AppIcon from "./AppIcon.vue";
import AppLoader from "./AppLoader.vue";
import { getReportDigest } from "../services/analytics";

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  initialDigest: { type: Object, default: null },
  reportDate: { type: String, default: null },
});

const emit = defineEmits(["close"]);
const router = useRouter();

const loading = ref(false);
const digestData = ref(null);
const activeTab = ref("courses"); // 'courses' | 'urgent' | 'completed'

const digest = computed(() => digestData.value || props.initialDigest || {});

const loadDeepDigest = async () => {
  if (!props.isOpen) return;
  loading.value = true;
  try {
    const { data } = await getReportDigest(props.reportDate || props.initialDigest?.report_date);
    if (data?.digest) {
      digestData.value = data.digest;
    }
  } catch {
    // Fall back to initialDigest if request fails
    if (props.initialDigest) {
      digestData.value = props.initialDigest;
    }
  } finally {
    loading.value = false;
  }
};

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      digestData.value = props.initialDigest;
      loadDeepDigest();
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
  }
);

onBeforeUnmount(() => {
  document.body.style.overflow = "";
});

const formattedDate = computed(() => {
  const dStr = digest.value?.report_date || props.reportDate;
  if (!dStr) return "Today's Summary";
  const date = new Date(dStr.includes("T") ? dStr : `${dStr}T00:00:00`);
  return isNaN(date.getTime())
    ? dStr
    : date.toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric", year: "numeric" });
});

const completionRate = computed(() => {
  const rate = digest.value?.completion_rate;
  if (typeof rate === "number") return rate;
  const tot = digest.value?.total_tasks || 0;
  const comp = digest.value?.completed_tasks || 0;
  return tot > 0 ? Math.round((comp / tot) * 100) : 0;
});

// SVG Circular Gauge calculations
const radius = 42;
const circumference = 2 * Math.PI * radius;
const strokeDashoffset = computed(() => {
  const percent = Math.min(100, Math.max(0, completionRate.value));
  return circumference - (percent / 100) * circumference;
});

const momentumBadgeClass = computed(() => {
  const rate = completionRate.value;
  if (rate >= 80) return "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800";
  if (rate >= 60) return "bg-brand-50 text-brand-700 border-brand-200 dark:bg-brand-950/60 dark:text-brand-300 dark:border-brand-800";
  if (rate >= 40) return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800";
  return "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700";
});

const goToTasks = () => {
  emit("close");
  router.push({ name: "tasks" });
};

const printDigest = () => {
  window.print();
};

const onKeydown = (e) => {
  if (e.key === "Escape" && props.isOpen) {
    emit("close");
  }
};

if (typeof window !== "undefined") {
  window.addEventListener("keydown", onKeydown);
}
onBeforeUnmount(() => {
  if (typeof window !== "undefined") {
    window.removeEventListener("keydown", onKeydown);
  }
});
</script>

<template>
  <Teleport to="body">
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 md:p-6 overflow-y-auto backdrop-blur-md bg-slate-900/60"
        role="dialog"
        aria-modal="true"
        aria-labelledby="digest-modal-title"
        @click.self="emit('close')"
      >
        <div
          class="surface-elevated relative w-full max-w-2xl overflow-hidden rounded-3xl border border-slate-200/90 bg-white/95 shadow-2xl backdrop-blur-xl dark:border-slate-800 dark:bg-night-surface/95 my-auto"
        >
          <!-- Modal Header Banner -->
          <div class="relative bg-gradient-to-r from-brand-700 via-indigo-600 to-academic-purple px-6 py-5 text-white shadow-md">
            <div class="flex items-start justify-between gap-4">
              <div class="flex items-center gap-3">
                <div class="flex h-11 w-11 flex-none items-center justify-center rounded-2xl bg-white/15 backdrop-blur-sm ring-1 ring-white/30 shadow-inner">
                  <AppIcon name="sparkles" :size="22" class="text-amber-300 animate-pulse" />
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="rounded-full bg-white/20 px-2.5 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wider text-white">
                      Productivity Digest
                    </span>
                    <span class="font-mono text-xs text-white/80">
                      {{ digest?.grade ? `Grade ${digest.grade}` : 'Verified Report' }}
                    </span>
                  </div>
                  <h2 id="digest-modal-title" class="mt-0.5 font-display text-xl font-bold tracking-tight text-white sm:text-2xl">
                    Daily Productivity Snapshot
                  </h2>
                </div>
              </div>

              <!-- Close Button -->
              <button
                type="button"
                class="rounded-xl p-1.5 text-white/80 hover:bg-white/20 hover:text-white transition-colors"
                aria-label="Close modal"
                @click="emit('close')"
              >
                <AppIcon name="x" :size="20" />
              </button>
            </div>

            <!-- Date Banner Subtitle -->
            <p class="mt-2 text-xs font-medium text-white/90 font-mono">
              📅 {{ formattedDate }}
            </p>
          </div>

          <!-- Loading Indicator overlay -->
          <div v-if="loading && !digestData" class="p-10">
            <AppLoader size="md" text="Compiling academic productivity metrics..." />
          </div>

          <!-- Digest Content Body -->
          <div v-else class="max-h-[75vh] overflow-y-auto p-5 sm:p-6 space-y-6">
            <!-- Hero Metric Section: Circular Gauge + 4 KPI Cards -->
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-12 sm:items-center rounded-2xl border border-slate-100 bg-slate-50/70 p-4 dark:border-slate-800/80 dark:bg-night-card/50">
              <!-- Left: Circular Completion Gauge -->
              <div class="sm:col-span-4 flex flex-col items-center justify-center py-2">
                <div class="relative flex items-center justify-center">
                  <svg class="h-28 w-28 -rotate-90 transform" viewBox="0 0 100 100">
                    <!-- Track Circle -->
                    <circle
                      cx="50"
                      cy="50"
                      :r="radius"
                      stroke-width="8"
                      class="stroke-slate-200 dark:stroke-slate-800"
                      fill="transparent"
                    />
                    <!-- Progress Circle -->
                    <circle
                      cx="50"
                      cy="50"
                      :r="radius"
                      stroke-width="8"
                      stroke-linecap="round"
                      stroke="url(#modalProgressGrad)"
                      :stroke-dasharray="circumference"
                      :stroke-dashoffset="strokeDashoffset"
                      fill="transparent"
                      class="transition-all duration-1000 ease-out"
                    />
                    <defs>
                      <linearGradient id="modalProgressGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#4f46e5" />
                        <stop offset="100%" stop-color="#10b981" />
                      </linearGradient>
                    </defs>
                  </svg>

                  <!-- Inner Score Display -->
                  <div class="absolute flex flex-col items-center justify-center text-center">
                    <span class="font-display text-2xl font-extrabold text-slate-900 dark:text-white leading-none">
                      {{ completionRate }}%
                    </span>
                    <span class="font-mono text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase mt-0.5">
                      Completed
                    </span>
                  </div>
                </div>

                <!-- Momentum Pill -->
                <span class="mt-2.5 inline-flex items-center gap-1 rounded-lg border px-2.5 py-1 text-xs font-bold" :class="momentumBadgeClass">
                  <AppIcon name="fire" :size="13" />
                  {{ digest?.momentum || 'Active Progress' }}
                </span>
              </div>

              <!-- Right: 4 Core Stat Tiles -->
              <div class="sm:col-span-8 grid grid-cols-2 gap-2.5">
                <!-- Tile 1: Total Workload -->
                <div class="surface-card p-3 rounded-xl border border-slate-200/70 dark:border-slate-800">
                  <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Total Workload</span>
                  <div class="mt-1 flex items-baseline justify-between">
                    <span class="font-display text-xl font-extrabold text-slate-900 dark:text-white">
                      {{ digest?.total_tasks || 0 }}
                    </span>
                    <span class="font-mono text-xs text-slate-400">tasks</span>
                  </div>
                </div>

                <!-- Tile 2: Completed -->
                <div class="surface-card p-3 rounded-xl border border-emerald-200/70 bg-emerald-50/40 dark:border-emerald-900/40 dark:bg-emerald-950/20">
                  <span class="text-[11px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">Completed</span>
                  <div class="mt-1 flex items-baseline justify-between">
                    <span class="font-display text-xl font-extrabold text-emerald-600 dark:text-emerald-300">
                      {{ digest?.completed_tasks || 0 }}
                    </span>
                    <span class="font-mono text-xs text-emerald-600/70 dark:text-emerald-400/70 font-semibold">
                      {{ digest?.total_tasks ? Math.round(((digest?.completed_tasks || 0) / digest.total_tasks) * 100) : 0 }}%
                    </span>
                  </div>
                </div>

                <!-- Tile 3: In Progress -->
                <div class="surface-card p-3 rounded-xl border border-indigo-200/70 bg-indigo-50/40 dark:border-indigo-900/40 dark:bg-indigo-950/20">
                  <span class="text-[11px] font-bold uppercase tracking-wider text-indigo-700 dark:text-indigo-400">In Progress</span>
                  <div class="mt-1 flex items-baseline justify-between">
                    <span class="font-display text-xl font-extrabold text-indigo-600 dark:text-indigo-300">
                      {{ digest?.in_progress_tasks || 0 }}
                    </span>
                    <span class="font-mono text-xs text-indigo-500 dark:text-indigo-400 font-semibold">active</span>
                  </div>
                </div>

                <!-- Tile 4: Overdue -->
                <div class="surface-card p-3 rounded-xl border border-rose-200/70 bg-rose-50/40 dark:border-rose-900/40 dark:bg-rose-950/20">
                  <span class="text-[11px] font-bold uppercase tracking-wider text-rose-700 dark:text-rose-400">Overdue</span>
                  <div class="mt-1 flex items-baseline justify-between">
                    <span class="font-display text-xl font-extrabold text-rose-600 dark:text-rose-400">
                      {{ digest?.overdue_tasks || 0 }}
                    </span>
                    <span class="font-mono text-xs text-rose-500 font-semibold">urgent</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Motivational Academic Quote Banner -->
            <div class="relative overflow-hidden rounded-2xl border border-brand-200/70 bg-gradient-to-r from-brand-50/80 via-indigo-50/60 to-purple-50/40 p-4 dark:border-brand-900/40 dark:from-brand-950/40 dark:via-indigo-950/30 dark:to-purple-950/20">
              <div class="flex items-start gap-3">
                <div class="flex h-8 w-8 flex-none items-center justify-center rounded-xl bg-brand-600 text-white shadow-sm">
                  <AppIcon name="academic" :size="16" />
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-xs font-bold uppercase tracking-wider text-brand-700 dark:text-brand-300">
                    Academic Momentum Insight
                  </p>
                  <p class="mt-1 text-xs italic leading-relaxed text-slate-700 dark:text-slate-300">
                    "{{ digest?.quote || 'Consistent daily study sprints build unstoppable academic momentum.' }}"
                  </p>
                </div>
              </div>
            </div>

            <!-- Interactive Tab Navigation -->
            <div>
              <div class="flex items-center gap-2 border-b border-slate-200/80 pb-2 dark:border-slate-800">
                <button
                  type="button"
                  class="rounded-xl px-3 py-1.5 text-xs font-bold transition-all"
                  :class="activeTab === 'courses' ? 'bg-brand-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'"
                  @click="activeTab = 'courses'"
                >
                  Course Workloads ({{ digest?.courses?.length || 0 }})
                </button>

                <button
                  type="button"
                  class="rounded-xl px-3 py-1.5 text-xs font-bold transition-all flex items-center gap-1.5"
                  :class="activeTab === 'urgent' ? 'bg-rose-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'"
                  @click="activeTab = 'urgent'"
                >
                  <span>Upcoming Due</span>
                  <span v-if="digest?.urgent_tasks?.length" class="rounded-full bg-rose-100 dark:bg-rose-950 px-1.5 py-0.2 text-[10px] text-rose-700 dark:text-rose-300">
                    {{ digest.urgent_tasks.length }}
                  </span>
                </button>

                <button
                  type="button"
                  class="rounded-xl px-3 py-1.5 text-xs font-bold transition-all"
                  :class="activeTab === 'completed' ? 'bg-emerald-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'"
                  @click="activeTab = 'completed'"
                >
                  Completed Highlights ({{ digest?.recent_completed?.length || 0 }})
                </button>
              </div>

              <!-- Tab 1: Course Breakdown -->
              <div v-if="activeTab === 'courses'" class="mt-3 space-y-2.5">
                <div v-if="!digest?.courses?.length" class="p-4 text-center text-xs text-slate-400">
                  No active courses enrolled yet.
                </div>
                <div
                  v-for="course in digest?.courses || []"
                  :key="course.id"
                  class="surface-card p-3 rounded-xl border border-slate-100 dark:border-slate-800"
                >
                  <div class="flex items-center justify-between text-xs mb-1.5">
                    <span class="flex items-center gap-2 font-bold text-slate-900 dark:text-white">
                      <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: course.color || '#4f46e5' }"></span>
                      <span>{{ course.name }}</span>
                      <span class="font-mono text-[10px] text-slate-400 uppercase">[{{ course.code }}]</span>
                    </span>
                    <span class="font-mono font-bold text-slate-600 dark:text-slate-300">
                      {{ course.completed }} / {{ course.total }} ({{ course.percentage }}%)
                    </span>
                  </div>
                  <!-- Progress Bar -->
                  <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                    <div
                      class="h-full rounded-full transition-all duration-500"
                      :style="{ width: `${course.percentage}%`, backgroundColor: course.color || '#4f46e5' }"
                    ></div>
                  </div>
                </div>
              </div>

              <!-- Tab 2: Urgent Tasks -->
              <div v-else-if="activeTab === 'urgent'" class="mt-3 space-y-2">
                <div v-if="!digest?.urgent_tasks?.length" class="p-4 text-center text-xs text-emerald-600 dark:text-emerald-400 font-semibold">
                  🎉 No overdue or high-priority deadlines pending!
                </div>
                <div
                  v-for="task in digest?.urgent_tasks || []"
                  :key="task.id"
                  class="flex items-center justify-between p-3 rounded-xl border border-rose-200/80 bg-rose-50/40 dark:border-rose-900/40 dark:bg-rose-950/20 text-xs"
                >
                  <div class="flex items-center gap-2.5 min-w-0">
                    <AppIcon name="alert" :size="15" class="text-rose-500 flex-none" />
                    <span class="font-bold text-slate-900 dark:text-white truncate">{{ task.title }}</span>
                  </div>
                  <span class="font-mono text-[11px] font-bold text-rose-600 dark:text-rose-400 flex-none ml-2">
                    Due: {{ task.due_date ? new Date(task.due_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : 'Soon' }}
                  </span>
                </div>
              </div>

              <!-- Tab 3: Completed Highlights -->
              <div v-else class="mt-3 space-y-2">
                <div v-if="!digest?.recent_completed?.length" class="p-4 text-center text-xs text-slate-400">
                  No completed tasks recorded for this report.
                </div>
                <div
                  v-for="task in digest?.recent_completed || []"
                  :key="task.id"
                  class="flex items-center justify-between p-3 rounded-xl border border-emerald-200/80 bg-emerald-50/40 dark:border-emerald-900/40 dark:bg-emerald-950/20 text-xs"
                >
                  <div class="flex items-center gap-2.5 min-w-0">
                    <AppIcon name="check-circle" :size="15" class="text-emerald-600 flex-none" />
                    <span class="font-bold text-slate-900 dark:text-white truncate">{{ task.title }}</span>
                  </div>
                  <span class="font-mono text-[10px] font-bold uppercase text-emerald-700 dark:text-emerald-300 flex-none ml-2">
                    Finished
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Modal Footer Actions -->
          <div class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200/80 bg-slate-50/80 px-6 py-4 dark:border-slate-800 dark:bg-night-card/80">
            <button
              type="button"
              class="btn-secondary text-xs gap-1.5"
              @click="printDigest"
            >
              <AppIcon name="printer" :size="15" />
              <span>Print / Save Digest</span>
            </button>

            <div class="flex items-center gap-2 ml-auto">
              <button
                type="button"
                class="btn-primary text-xs gap-1.5"
                @click="goToTasks"
              >
                <AppIcon name="tasks" :size="15" />
                <span>Jump to Task Ledger</span>
              </button>

              <button
                type="button"
                class="btn-ghost text-xs"
                @click="emit('close')"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>
