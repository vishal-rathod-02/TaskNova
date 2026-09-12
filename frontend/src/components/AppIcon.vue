<script setup>
import { computed } from "vue";

const props = defineProps({
  name: { type: String, required: true },
  size: { type: Number, default: 20 },
});

const paths = {
  dashboard: '<path d="M3 12h8V3H3v9zm10 9h8v-9h-8v9zM3 21h8v-6H3v6zm10-15v6h8V6h-8z" />',
  projects: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z" />',
  tasks: '<path d="M4 6h16M4 12h16M4 18h10" />',
  admin: '<circle cx="12" cy="8" r="3.2" /><path d="M5 20c1.2-3.4 3.9-5 7-5s5.8 1.6 7 5" />',
  plus: '<path d="M12 5v14M5 12h14" />',
  refresh: '<path d="M20 12a8 8 0 1 1-2.3-5.6M20 3v4h-4" />',
  check: '<path d="M4 12.5l5 5L20 6.5" />',
  clock: '<circle cx="12" cy="12" r="8.5" /><path d="M12 7.5V12l3 2" />',
  info: '<circle cx="12" cy="12" r="8.5" /><path d="M12 11v5M12 8h.01" />',
  bell: '<path d="M6 9a6 6 0 1 1 12 0c0 5 2 6 2 6H4s2-1 2-6" /><path d="M10 20a2 2 0 0 0 4 0" />',
  chevron: '<path d="M6 9l6 6 6-6" />',
  inbox: '<path d="M3 13l2.5-8h13L21 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-6z" /><path d="M3 13h6l1.5 2.5h3L15 13h6" />',
  alert: '<path d="M12 3l10 17H2L12 3z" /><path d="M12 10v4M12 17.5h.01" />',
};

const iconBody = computed(() => paths[props.name] || paths.info);
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.5"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
    v-html="iconBody"
  />
</template>
