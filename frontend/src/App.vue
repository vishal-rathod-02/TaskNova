<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppIcon from "./components/AppIcon.vue";
import ToastNotifications from "./components/ToastNotifications.vue";
import { useTheme } from "./composables/useTheme";
import { useAuthStore } from "./stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const { isDark, toggleTheme } = useTheme();

const showShell = computed(() => authStore.isAuthenticated && !["login", "register"].includes(route.name));

const logout = () => {
  authStore.logout();
  router.push({ name: "login" });
};
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
        <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link gap-2"><AppIcon name="admin" :size="16" />Admin</router-link>
      </nav>
      <div class="mt-auto border-t border-slate/20 pt-5 dark:border-slate/30">
        <p class="text-sm font-medium text-ink dark:text-[#E7E9ED]">{{ authStore.user?.full_name || "User" }}</p>
        <p class="mt-1 data-label">{{ authStore.user?.role || "user" }}</p>
        <button class="mt-5 min-h-11 text-sm font-medium text-slate underline decoration-slate/50 underline-offset-4 hover:text-ink dark:text-[#9AA3B2] dark:hover:text-[#E7E9ED]" type="button" @click="toggleTheme">{{ isDark ? "Use daylight" : "Use night shift" }}</button>
        <button class="mt-2 block min-h-11 text-sm font-medium text-ember hover:underline dark:text-ember-dark" type="button" @click="logout">Sign out</button>
      </div>
    </aside>
    <main :class="showShell ? 'pb-20 md:pl-64 md:pb-0' : ''">
      <router-view />
    </main>
    <nav v-if="showShell" class="fixed inset-x-0 bottom-0 z-40 grid border-t border-slate/20 bg-white px-4 dark:border-slate/30 dark:bg-night-surface md:hidden" :class="authStore.isAdmin ? 'grid-cols-4' : 'grid-cols-3'" aria-label="Mobile navigation">
      <router-link to="/" class="nav-link justify-center gap-1"><AppIcon name="dashboard" :size="16" />Dashboard</router-link>
      <router-link to="/projects" class="nav-link justify-center gap-1"><AppIcon name="projects" :size="16" />Projects</router-link>
      <router-link to="/tasks" class="nav-link justify-center gap-1"><AppIcon name="tasks" :size="16" />Tasks</router-link>
      <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link justify-center gap-1"><AppIcon name="admin" :size="16" />Admin</router-link>
    </nav>
    <button v-if="showShell" class="fixed right-4 top-4 z-30 min-h-11 border border-slate/40 bg-white px-3 text-sm font-medium text-ink dark:border-slate/50 dark:bg-night-surface dark:text-[#E7E9ED] md:hidden" type="button" @click="toggleTheme">{{ isDark ? "Daylight" : "Night shift" }}</button>
    <ToastNotifications />
  </div>
</template>
