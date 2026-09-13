<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import AppErrorBoundary from "./components/AppErrorBoundary.vue";
import AppIcon from "./components/AppIcon.vue";
import BrandLogo from "./components/BrandLogo.vue";
import FocusTimerModal from "./components/FocusTimerModal.vue";
import ToastNotifications from "./components/ToastNotifications.vue";
import UserMenu from "./components/UserMenu.vue";
import { useTheme } from "./composables/useTheme";
import { useAuthStore } from "./stores/auth";
import { useNotificationStore } from "./stores/notifications";
import { useTimerStore } from "./stores/timer";

const route = useRoute();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const timerStore = useTimerStore();
const { isDark, toggleTheme } = useTheme();

const isTimerOpen = ref(false);

const showShell = computed(() => authStore.isAuthenticated && !["login", "register"].includes(route.name));

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated) {
      notificationStore.fetchNotifications().catch(() => {});
    }
  },
  { immediate: true }
);
</script>

<template>
  <div class="min-h-screen bg-paper font-sans text-ink transition-colors duration-200 dark:bg-night-bg dark:text-slate-100">
    <!-- Desktop Left Sidebar -->
    <aside
      v-if="showShell"
      class="fixed inset-y-0 left-0 hidden w-64 flex-col border-r border-slate-200/80 bg-white/95 px-5 py-6 backdrop-blur-xl dark:border-slate-800/80 dark:bg-night-surface/95 md:flex z-30"
    >
      <!-- Workspace Brand Logo -->
      <div class="px-1">
        <BrandLogo size="md" tagline="Academic Workplace" />
      </div>

      <!-- Quick Study Timer Action Button with Live Clock Display -->
      <div class="mt-6 px-1">
        <button
          type="button"
          class="flex w-full items-center justify-between rounded-xl border p-2.5 text-xs font-semibold transition-all duration-300"
          :class="[
            timerStore.isUrgent
              ? 'border-rose-400 bg-rose-100/90 text-rose-900 shadow-[0_0_15px_rgba(244,63,94,0.35)] animate-pulse dark:border-rose-500 dark:bg-rose-950/80 dark:text-rose-200'
              : (timerStore.isEndingSoon
                ? 'border-amber-400 bg-amber-100/90 text-amber-900 dark:border-amber-500 dark:bg-amber-950/80 dark:text-amber-200'
                : (timerStore.isRunning
                  ? 'border-brand-400 bg-brand-100/90 text-brand-900 shadow-sm dark:border-brand-500 dark:bg-brand-950/80 dark:text-brand-200'
                  : 'border-brand-200 bg-brand-50/60 text-brand-700 hover:bg-brand-100 hover:border-brand-300 dark:border-brand-900/40 dark:bg-brand-950/40 dark:text-brand-300 dark:hover:bg-brand-900/50'))
          ]"
          @click="isTimerOpen = true"
        >
          <span class="flex items-center gap-2">
            <AppIcon
              name="timer"
              :size="16"
              :class="timerStore.isUrgent ? 'text-rose-600 animate-spin' : (timerStore.isEndingSoon ? 'text-amber-600 animate-bounce' : 'text-brand-600 dark:text-brand-400')"
            />
            <span>{{ timerStore.isRunning ? (timerStore.isUrgent ? 'Final Sprint!' : timerStore.currentModeLabel) : 'Study Focus Timer' }}</span>
          </span>
          <span
            class="rounded px-1.5 py-0.5 font-mono text-[11px] font-bold"
            :class="timerStore.isUrgent
              ? 'bg-rose-600 text-white animate-tick-pop'
              : (timerStore.isEndingSoon
                ? 'bg-amber-500 text-white'
                : (timerStore.isRunning ? 'bg-brand-600 text-white' : 'bg-brand-200/60 dark:bg-brand-900/80'))"
          >
            {{ timerStore.formattedTime }}
          </span>
        </button>
      </div>

      <!-- Navigation Links -->
      <nav class="mt-6 space-y-1.5" aria-label="Primary navigation">
        <router-link to="/" class="nav-item">
          <AppIcon name="dashboard" :size="18" />
          <span>Dashboard</span>
        </router-link>

        <router-link to="/projects" class="nav-item">
          <AppIcon name="projects" :size="18" />
          <span>Courses & Projects</span>
        </router-link>

        <router-link to="/tasks" class="nav-item">
          <AppIcon name="tasks" :size="18" />
          <span>Task Ledger & Kanban</span>
        </router-link>

        <router-link to="/calendar" class="nav-item">
          <AppIcon name="calendar" :size="18" />
          <span>Academic Calendar</span>
        </router-link>

        <router-link to="/notifications" class="nav-item justify-between">
          <span class="flex items-center gap-3">
            <AppIcon name="bell" :size="18" />
            <span>Notification Inbox</span>
          </span>
          <span
            v-if="notificationStore.unreadCount"
            class="flex h-5 min-w-5 items-center justify-center rounded-full bg-rose-500 px-1.5 font-mono text-[10px] font-extrabold text-white shadow-sm"
          >
            {{ notificationStore.unreadCount }}
          </span>
        </router-link>

        <router-link v-if="authStore.isAdmin" to="/admin" class="nav-item">
          <AppIcon name="admin" :size="18" />
          <span>User Directory</span>
        </router-link>
      </nav>

      <!-- Bottom User Profile Section (Desktop) -->
      <div class="mt-auto border-t border-slate-100 pt-4 dark:border-slate-800 space-y-2">
        <UserMenu
          :is-dark="isDark"
          placement="bottom"
          @toggle-theme="toggleTheme"
          @open-timer="isTimerOpen = true"
        />
        <div class="flex items-center justify-between px-2 text-[10px] font-mono text-slate-400 dark:text-slate-500">
          <span>TaskNova Workspace</span>
          <span class="rounded bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 font-bold">v1.0</span>
        </div>
      </div>
    </aside>

    <!-- Mobile Top Navigation Header with Streamlined User Menu -->
    <header
      v-if="showShell"
      class="sticky top-0 z-30 flex min-h-14 items-center justify-between border-b border-slate-200/80 bg-white/90 px-3.5 backdrop-blur-md dark:border-slate-800 dark:bg-night-surface/90 md:hidden"
    >
      <!-- Brand Logo on Mobile -->
      <BrandLogo size="sm" :show-tagline="false" />

      <!-- Clean Header Controls -->
      <div class="flex items-center gap-2">
        <!-- Live Countdown Pill (Active only when timer is running) -->
        <button
          v-if="timerStore.isRunning"
          type="button"
          class="flex items-center gap-1.5 rounded-xl px-2.5 py-1 text-xs font-bold transition-all duration-200 shadow-sm"
          :class="[
            timerStore.isUrgent
              ? 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300 animate-pulse border border-rose-300 dark:border-rose-800'
              : (timerStore.isEndingSoon
                ? 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300 border border-amber-300 dark:border-amber-800'
                : 'text-brand-700 dark:text-brand-300 bg-brand-50 dark:bg-brand-950/70 border border-brand-200 dark:border-brand-900')
          ]"
          title="Open Focus Timer"
          @click="isTimerOpen = true"
        >
          <AppIcon name="timer" :size="15" :class="timerStore.isUrgent ? 'animate-spin' : ''" />
          <span class="font-mono text-xs font-bold">{{ timerStore.formattedTime }}</span>
        </button>

        <!-- Mobile User Profile & Settings Menu -->
        <UserMenu
          :is-dark="isDark"
          :compact="true"
          placement="top"
          @toggle-theme="toggleTheme"
          @open-timer="isTimerOpen = true"
        />
      </div>
    </header>

    <!-- Main Content Area -->
    <main :class="showShell ? 'pb-24 md:pl-64 md:pb-12' : ''">
      <AppErrorBoundary :key="route.fullPath">
        <router-view />
      </AppErrorBoundary>
    </main>

    <!-- Mobile Bottom Navigation Bar -->
    <nav
      v-if="showShell"
      class="fixed inset-x-0 bottom-0 z-40 grid border-t border-slate-200/80 bg-white/95 px-2 py-1 shadow-lg backdrop-blur-xl dark:border-slate-800 dark:bg-night-surface/95 md:hidden"
      :class="authStore.isAdmin ? 'grid-cols-6' : 'grid-cols-5'"
      aria-label="Mobile navigation"
    >
      <router-link to="/" class="mobile-nav-item">
        <AppIcon name="dashboard" :size="18" />
        <span>Dashboard</span>
      </router-link>

      <router-link to="/projects" class="mobile-nav-item">
        <AppIcon name="projects" :size="18" />
        <span>Courses</span>
      </router-link>

      <router-link to="/tasks" class="mobile-nav-item">
        <AppIcon name="tasks" :size="18" />
        <span>Tasks</span>
      </router-link>

      <router-link to="/calendar" class="mobile-nav-item">
        <AppIcon name="calendar" :size="18" />
        <span>Calendar</span>
      </router-link>

      <router-link to="/notifications" class="mobile-nav-item relative">
        <AppIcon name="bell" :size="18" />
        <span>Inbox</span>
        <span
          v-if="notificationStore.unreadCount"
          class="absolute right-3 top-1 flex h-3.5 min-w-3.5 items-center justify-center rounded-full bg-rose-500 px-1 font-mono text-[8px] font-bold text-white"
        >
          {{ notificationStore.unreadCount }}
        </span>
      </router-link>

      <router-link v-if="authStore.isAdmin" to="/admin" class="mobile-nav-item">
        <AppIcon name="admin" :size="18" />
        <span>Directory</span>
      </router-link>
    </nav>

    <!-- Global Study Focus Timer Modal -->
    <FocusTimerModal :is-open="isTimerOpen" @close="isTimerOpen = false" />

    <!-- Global Toast Notifications Stack -->
    <ToastNotifications />
  </div>
</template>
