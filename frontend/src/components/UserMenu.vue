<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useNotificationStore } from "../stores/notifications";
import { useTimerStore } from "../stores/timer";
import AppIcon from "./AppIcon.vue";

const props = defineProps({
  isDark: { type: Boolean, required: true },
  placement: { type: String, default: "bottom" },
  compact: { type: Boolean, default: false },
});

const emit = defineEmits(["toggle-theme", "open-timer"]);

const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const timerStore = useTimerStore();
const router = useRouter();

const open = ref(false);
const menuRef = ref(null);

const close = () => {
  open.value = false;
};

const onDocumentClick = (event) => {
  if (menuRef.value && !menuRef.value.contains(event.target)) {
    close();
  }
};

const onKeydown = (event) => {
  if (event.key === "Escape") {
    close();
  }
};

if (typeof document !== "undefined") {
  document.addEventListener("click", onDocumentClick);
  document.addEventListener("keydown", onKeydown);
}

onBeforeUnmount(() => {
  document.removeEventListener("click", onDocumentClick);
  document.removeEventListener("keydown", onKeydown);
});

const signOut = () => {
  close();
  authStore.logout();
  router.push({ name: "login" });
};
</script>

<template>
  <div ref="menuRef" class="relative">
    <!-- Compact Avatar Button for Mobile Header -->
    <button
      v-if="compact"
      class="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-600 to-academic-purple font-display text-xs font-bold text-white shadow-sm ring-2 ring-brand-500/20 transition-all duration-200 active:scale-95 hover:shadow-md"
      type="button"
      :aria-expanded="open"
      aria-haspopup="menu"
      title="User Account & Settings"
      @click="open = !open"
    >
      <span>{{ (authStore.user?.full_name || "U").charAt(0).toUpperCase() }}</span>

      <!-- Unread Notification Indicator Dot on Avatar -->
      <span
        v-if="notificationStore.unreadCount"
        class="absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-rose-500 ring-2 ring-white dark:ring-night-surface"
      >
        <span class="h-1.5 w-1.5 rounded-full bg-white"></span>
      </span>
    </button>

    <!-- Full Width Button for Desktop Sidebar -->
    <button
      v-else
      class="flex min-h-12 w-full items-center gap-3 rounded-xl border border-transparent p-2 text-left transition-all duration-150 hover:border-slate-200 hover:bg-slate-100/80 dark:hover:border-slate-800 dark:hover:bg-slate-800/60"
      type="button"
      :aria-expanded="open"
      aria-haspopup="menu"
      @click="open = !open"
    >
      <!-- Avatar Circle with Gradient -->
      <span
        class="flex h-10 w-10 flex-none items-center justify-center rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-600 to-academic-purple font-display text-base font-bold text-white shadow-sm"
        aria-hidden="true"
      >
        {{ (authStore.user?.full_name || "U").charAt(0).toUpperCase() }}
      </span>

      <!-- User Information -->
      <span class="min-w-0 flex-1">
        <span class="block truncate text-sm font-bold text-slate-900 dark:text-white">
          {{ authStore.user?.full_name || "Student User" }}
        </span>
        <span class="flex items-center gap-1 font-mono text-[11px] font-semibold uppercase text-brand-600 dark:text-brand-400">
          <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
          {{ authStore.user?.role === 'admin' ? 'Administrator' : 'Student Account' }}
        </span>
      </span>

      <AppIcon
        name="chevron"
        :size="16"
        class="text-slate-400 transition-transform duration-200 dark:text-slate-500"
        :class="{ 'rotate-180': open }"
      />
    </button>

    <!-- Modern Elevated Animated Dropdown Menu -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform scale-95 opacity-0 -translate-y-2"
      enter-to-class="transform scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform scale-100 opacity-100 translate-y-0"
      leave-to-class="transform scale-95 opacity-0 -translate-y-2"
    >
      <div
        v-if="open"
        role="menu"
        aria-label="Account options"
        :class="placement === 'top'
          ? 'surface-elevated absolute right-0 top-full mt-2 w-72 z-50 overflow-hidden rounded-2xl border border-slate-200/90 bg-white/95 p-1.5 shadow-2xl backdrop-blur-xl dark:border-slate-800 dark:bg-night-surface/95'
          : 'surface-elevated absolute inset-x-0 bottom-full z-50 mb-2 w-full overflow-hidden rounded-2xl border border-slate-200/90 bg-white/95 p-1.5 shadow-2xl backdrop-blur-xl dark:border-slate-800 dark:bg-night-surface/95'"
      >
        <!-- User Info Card Header -->
        <div class="rounded-xl bg-slate-50/80 p-3 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800/80">
          <div class="flex items-center gap-2.5">
            <span class="flex h-9 w-9 flex-none items-center justify-center rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 font-display text-xs font-bold text-white shadow-sm">
              {{ (authStore.user?.full_name || "U").charAt(0).toUpperCase() }}
            </span>
            <div class="min-w-0 flex-1">
              <div class="flex items-center justify-between gap-1">
                <p class="truncate text-sm font-bold text-slate-900 dark:text-white leading-tight">
                  {{ authStore.user?.full_name }}
                </p>
                <span class="rounded bg-brand-100/80 dark:bg-brand-950/80 px-1.5 py-0.5 font-mono text-[9px] font-bold text-brand-700 dark:text-brand-300">
                  v1.0
                </span>
              </div>
              <p class="font-mono text-[11px] text-slate-500 dark:text-slate-400 truncate mt-0.5">
                {{ authStore.user?.email }}
              </p>
            </div>
          </div>
          <div class="mt-2.5 flex items-center justify-between border-t border-slate-200/60 pt-2 text-[10px] font-mono text-slate-500 dark:border-slate-800 dark:text-slate-400">
            <span>ROLE</span>
            <span class="font-bold text-brand-600 dark:text-brand-400 uppercase">
              {{ authStore.user?.role === 'admin' ? 'System Administrator' : 'Active Student' }}
            </span>
          </div>
        </div>

        <!-- Interactive Action Items -->
        <div class="py-1.5 space-y-1">
          <!-- Focus Study Timer Trigger -->
          <button
            role="menuitem"
            class="flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
            type="button"
            @click="emit('open-timer'); close()"
          >
            <span class="flex items-center gap-2.5">
              <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300">
                <AppIcon name="timer" :size="15" />
              </span>
              <span>Study Focus Timer</span>
            </span>

            <span
              class="rounded-md px-2 py-0.5 font-mono text-[10px] font-bold"
              :class="timerStore.isRunning ? 'bg-brand-600 text-white animate-pulse' : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'"
            >
              {{ timerStore.formattedTime }}
            </span>
          </button>

          <!-- Notification Center Link -->
          <router-link
            to="/notifications"
            role="menuitem"
            class="flex items-center justify-between rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
            @click="close"
          >
            <span class="flex items-center gap-2.5">
              <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-300">
                <AppIcon name="bell" :size="15" />
              </span>
              <span>Notification Inbox</span>
            </span>

            <span
              v-if="notificationStore.unreadCount"
              class="rounded-full bg-rose-500 px-2 py-0.5 font-mono text-[10px] font-bold text-white shadow-sm"
            >
              {{ notificationStore.unreadCount }} new
            </span>
          </router-link>

          <!-- Daylight / Night Shift Toggle Row with Animated Switch -->
          <button
            role="menuitem"
            class="flex w-full items-center justify-between rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
            type="button"
            @click="emit('toggle-theme')"
          >
            <span class="flex items-center gap-2.5">
              <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-50 text-amber-600 dark:bg-amber-950/60 dark:text-amber-300">
                <AppIcon :name="props.isDark ? 'sun' : 'moon'" :size="15" />
              </span>
              <span>{{ props.isDark ? "Daylight Mode" : "Night Shift Mode" }}</span>
            </span>

            <!-- Modern Switch Pill Component -->
            <div
              class="relative h-5 w-9 rounded-full transition-colors duration-200 p-0.5"
              :class="props.isDark ? 'bg-brand-600' : 'bg-slate-300 dark:bg-slate-700'"
            >
              <div
                class="h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-200"
                :class="props.isDark ? 'translate-x-4' : 'translate-x-0'"
              ></div>
            </div>
          </button>
        </div>

        <!-- Logout Action Button -->
        <div class="border-t border-slate-100 pt-1.5 dark:border-slate-800">
          <button
            role="menuitem"
            class="flex w-full items-center justify-between rounded-xl bg-rose-50/80 px-3.5 py-2.5 text-left text-xs font-bold text-rose-600 transition-all duration-200 hover:bg-rose-100 dark:bg-rose-950/40 dark:text-rose-400 dark:hover:bg-rose-900/60"
            type="button"
            @click="signOut"
          >
            <span class="flex items-center gap-2">
              <AppIcon name="arrow-right" :size="15" />
              <span>Log Out</span>
            </span>
            <span class="font-mono text-[10px] uppercase font-bold tracking-wider opacity-75">End Session</span>
          </button>
        </div>

        <!-- Release Version Tag -->
        <div class="mt-1 flex items-center justify-between px-2 pt-0.5 text-[10px] font-mono text-slate-400 dark:text-slate-500">
          <span>TaskNova Academic</span>
          <span class="font-semibold text-slate-500 dark:text-slate-400">v1.0.0</span>
        </div>
      </div>
    </transition>
  </div>
</template>

