<script setup>
import { onBeforeUnmount, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import AppIcon from "./AppIcon.vue";

const props = defineProps({
  isDark: { type: Boolean, required: true },
});

const emit = defineEmits(["toggle-theme"]);

const authStore = useAuthStore();
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
    <button
      class="flex min-h-11 w-full items-center gap-3 border border-transparent px-1 py-2 text-left transition-colors hover:border-slate/20"
      type="button"
      :aria-expanded="open"
      aria-haspopup="menu"
      @click="open = !open"
    >
      <span class="grid h-9 w-9 flex-none place-items-center border border-slate/30 font-display text-base font-semibold text-ink dark:border-slate/40 dark:text-[#E7E9ED]" aria-hidden="true">
        {{ (authStore.user?.full_name || "U").charAt(0).toUpperCase() }}
      </span>
      <span class="min-w-0 flex-1">
        <span class="block truncate text-sm font-medium text-ink dark:text-[#E7E9ED]">{{ authStore.user?.full_name || "User" }}</span>
        <span class="data-label block">{{ authStore.user?.role || "user" }}</span>
      </span>
      <AppIcon name="chevron" :size="16" class="text-slate transition-transform dark:text-[#9AA3B2]" :class="{ 'rotate-180': open }" />
    </button>

    <div
      v-if="open"
      role="menu"
      aria-label="Account options"
      class="surface absolute inset-x-0 bottom-full z-50 mb-2 grid max-h-[70vh] overflow-y-auto py-1 shadow-sm"
    >
      <div class="border-b border-slate/20 px-4 py-3 dark:border-slate/30">
        <p class="truncate text-sm font-medium text-ink dark:text-[#E7E9ED]">{{ authStore.user?.full_name }}</p>
        <p class="data-label mt-0.5 truncate">{{ authStore.user?.email }}</p>
      </div>
      <router-link to="/notifications" role="menuitem" class="flex min-h-11 items-center gap-2 px-4 text-sm text-ink hover:bg-paper dark:text-[#E7E9ED] dark:hover:bg-white/5" @click="close">
        <AppIcon name="bell" :size="16" />Notification inbox
      </router-link>
      <button role="menuitem" class="flex min-h-11 items-center gap-2 px-4 text-left text-sm text-ink hover:bg-paper dark:text-[#E7E9ED] dark:hover:bg-white/5" type="button" @click="emit('toggle-theme'); close()">
        <AppIcon name="refresh" :size="16" />{{ props.isDark ? "Use daylight" : "Use night shift" }}
      </button>
      <button role="menuitem" class="flex min-h-11 items-center gap-2 px-4 text-left text-sm font-medium text-ember hover:bg-ember/10 dark:text-ember-dark" type="button" @click="signOut">
        Sign out
      </button>
    </div>
  </div>
</template>
