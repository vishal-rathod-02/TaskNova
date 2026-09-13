<script setup>
import { computed } from "vue";

const props = defineProps({
  size: { type: String, default: "md" }, // 'sm', 'md', 'lg', 'xl'
  showTagline: { type: Boolean, default: true },
  showText: { type: Boolean, default: true },
  tagline: { type: String, default: "Academic Workplace" },
  isLink: { type: Boolean, default: true },
  to: { type: String, default: "/" },
});

const iconSizeClass = computed(() => {
  switch (props.size) {
    case "sm":
      return "h-8 w-8 rounded-lg p-1";
    case "lg":
      return "h-12 w-12 rounded-2xl p-2.5";
    case "xl":
      return "h-16 w-16 rounded-2xl p-3";
    case "md":
    default:
      return "h-10 w-10 rounded-xl p-2";
  }
});

const titleSizeClass = computed(() => {
  switch (props.size) {
    case "sm":
      return "text-base";
    case "lg":
      return "text-2xl";
    case "xl":
      return "text-3xl";
    case "md":
    default:
      return "text-lg";
  }
});

const taglineSizeClass = computed(() => {
  switch (props.size) {
    case "sm":
      return "text-[9px]";
    case "lg":
      return "text-[11px]";
    case "xl":
      return "text-xs";
    case "md":
    default:
      return "text-[10px]";
  }
});
</script>

<template>
  <component
    :is="isLink ? 'router-link' : 'div'"
    :to="isLink ? to : undefined"
    class="group inline-flex items-center gap-2.5 transition-transform duration-150 select-none"
  >
    <!-- Vector Brand Mark Tile -->
    <div
      :class="iconSizeClass"
      class="relative flex flex-none items-center justify-center bg-gradient-to-tr from-brand-700 via-indigo-600 to-academic-purple text-white shadow-sm ring-1 ring-white/20 transition-all duration-200 group-hover:scale-105 group-hover:shadow-md"
    >
      <svg
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        class="h-full w-full"
      >
        <!-- Academic Mortarboard Cap Facet -->
        <path
          d="M16 3.5L29 9.5L16 15.5L3 9.5L16 3.5Z"
          fill="#ffffff"
          opacity="0.95"
        />

        <!-- Cap Lower Shadow Foundation -->
        <path
          d="M7 12.5V19C7 22.5 11 25.5 16 25.5C21 25.5 25 22.5 25 19V12.5L16 16.5L7 12.5Z"
          fill="#c7d2fe"
          opacity="0.75"
        />

        <!-- Radiant Nova Core Spark -->
        <path
          d="M16 6L17.2 11.5L22.5 12.8L17.2 14L16 19.5L14.8 14L9.5 12.8L14.8 11.5L16 6Z"
          fill="#4f46e5"
        />

        <!-- Central Spark Dot -->
        <circle cx="16" cy="12.8" r="1.5" fill="#ffffff" />
      </svg>
    </div>

    <!-- Typography Text -->
    <div v-if="showText" class="min-w-0">
      <span
        :class="titleSizeClass"
        class="block font-display font-extrabold tracking-tight text-slate-900 leading-tight group-hover:text-brand-600 dark:text-white dark:group-hover:text-brand-300 transition-colors"
      >
        Task<span class="text-brand-600 dark:text-brand-400">Nova</span>
      </span>
      <span
        v-if="showTagline"
        :class="taglineSizeClass"
        class="block font-mono font-bold tracking-wider uppercase text-brand-600 dark:text-brand-400 -mt-0.5"
      >
        {{ tagline }}
      </span>
    </div>
  </component>
</template>

