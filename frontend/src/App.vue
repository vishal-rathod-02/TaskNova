<script setup>
import { computed, watch } from "vue";
import { useRoute } from "vue-router";
import AppErrorBoundary from "./components/AppErrorBoundary.vue";
import AppIcon from "./components/AppIcon.vue";
import ToastNotifications from "./components/ToastNotifications.vue";
import UserMenu from "./components/UserMenu.vue";
import { useTheme } from "./composables/useTheme";
import { useAuthStore } from "./stores/auth";
import { useNotificationStore } from "./stores/notifications";

const route = useRoute();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const { isDark, toggleTheme } = useTheme();

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
  <div class="min-h-screen bg-paper dark:bg-night-bg">
    <aside v-if="showShell" class="fixed inset-y-0 left-0 hidden w-64 flex-col border-r border-slate/20 bg-white px-6 py-8 dark:border-slate/30 dark:bg-night-surface md:flex">
      <router-link to="/" class="font-display text-[28px] font-semibold leading-8 text-ink dark:text-[#E7E9ED]">TaskNova</router-link>
      <p class="mt-2 text-sm leading-5 text-slate dark:text-[#9AA3B2]">A running account of work.</p>
      <nav class="mt-10 grid gap-2" aria-label="Primary navigation">
        <router-link to="/" class="nav-link gap-2"><AppIcon name="dashboard" :size="16" />Dashboard</router-link>
        <router-link to="/projects" class="nav-link gap-2"><AppIcon name="projects" :size="16" />Projects</router-link>
        <router-link to="/tasks" class="nav-link gap-2"><AppIcon name="tasks" :size="16" />Tasks</router-link>
        <router-link to="/notifications" class="nav-link gap-2">
          <AppIcon name="bell" :size="16" />Inbox
          <span v-if="notificationStore.unreadCount" class="data-label ml-auto border border-ember/40 px-1.5 py-0.5 text-ember dark:border-ember-dark/50 dark:text-ember-dark">{{ notificationStore.unreadCount }}</span>
        </router-link>
        <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link gap-2"><AppIcon name="admin" :size="16" />Admin</router-link>
      </nav>
      <div class="mt-auto border-t border-slate/20 pt-3 dark:border-slate/30">
        <UserMenu :is-dark="isDark" @toggle-theme="toggleTheme" />
      </div>
    </aside>
    <div v-if="showShell" class="sticky top-0 z-30 flex min-h-11 items-center gap-2 border-b border-slate/20 bg-white px-4 py-2 dark:border-slate/30 dark:bg-night-surface md:hidden">
      <router-link to="/" class="font-display text-lg font-semibold leading-6 text-ink dark:text-[#E7E9ED]">TaskNova</router-link>
      <span class="ml-auto flex items-center gap-1">
        <router-link to="/notifications" class="relative grid min-h-11 min-w-11 place-items-center px-2 text-slate hover:text-ink dark:text-[#9AA3B2] dark:hover:text-[#E7E9ED]" aria-label="Notification inbox">
          <AppIcon name="bell" :size="20" />
          <span v-if="notificationStore.unreadCount" class="absolute right-0.5 top-1 grid min-h-5 min-w-5 place-items-center bg-ember px-1 font-mono text-[11px] font-medium text-white dark:bg-ember-dark dark:text-ink">{{ notificationStore.unreadCount }}</span>
        </router-link>
        <button class="min-h-11 px-2 text-xs font-medium text-slate hover:text-ink dark:text-[#9AA3B2] dark:hover:text-[#E7E9ED]" type="button" @click="toggleTheme">{{ isDark ? "Daylight" : "Night shift" }}</button>
      </span>
    </div>
    <main :class="showShell ? 'pb-20 md:pl-64 md:pb-0' : ''">
      <AppErrorBoundary :key="route.fullPath">
        <router-view />
      </AppErrorBoundary>
    </main>
    <nav v-if="showShell" class="mobile-nav fixed inset-x-0 bottom-0 z-40 grid border-t border-slate/20 bg-white px-2 dark:border-slate/30 dark:bg-night-surface md:hidden" :class="authStore.isAdmin ? 'grid-cols-5' : 'grid-cols-4'" aria-label="Mobile navigation">
      <router-link to="/" class="nav-link justify-center gap-1"><AppIcon name="dashboard" :size="16" />Dashboard</router-link>
      <router-link to="/projects" class="nav-link justify-center gap-1"><AppIcon name="projects" :size="16" />Projects</router-link>
      <router-link to="/tasks" class="nav-link justify-center gap-1"><AppIcon name="tasks" :size="16" />Tasks</router-link>
      <router-link to="/notifications" class="nav-link justify-center gap-1"><AppIcon name="bell" :size="16" />Inbox</router-link>
      <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link justify-center gap-1"><AppIcon name="admin" :size="16" />Admin</router-link>
    </nav>
    <ToastNotifications />
  </div>
</template>
