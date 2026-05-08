<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "./stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const showShell = computed(() => authStore.isAuthenticated && !["login", "register"].includes(route.name));

const logout = () => {
  authStore.logout();
  router.push({ name: "login" });
};
</script>

<template>
  <div class="app-layout">
    <aside v-if="showShell" class="sidebar">
      <h1>TaskNova</h1>
      <router-link to="/" class="nav-link">Dashboard</router-link>
      <router-link to="/projects" class="nav-link">Projects</router-link>
      <router-link to="/tasks" class="nav-link">Tasks</router-link>
      <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link">Admin</router-link>
      <div style="margin-top: auto; padding: 6px 8px">
        <div class="muted" style="font-size: 12px; margin-bottom: 8px">
          Signed in as {{ authStore.user?.full_name || "User" }}
        </div>
        <button class="danger" style="width: 100%" @click="logout">Logout</button>
      </div>
    </aside>
    <main :class="showShell ? 'content with-shell' : 'content'">
      <router-view />
    </main>
  </div>
</template>
