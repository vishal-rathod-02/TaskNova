<script setup>
import { computed } from "vue";

const props = defineProps({
  size: { type: String, default: "md" }, // 'sm', 'md', 'lg', 'fullscreen'
  text: { type: String, default: "" },
  showCard: { type: Boolean, default: false },
});

const sizeClass = computed(() => {
  switch (props.size) {
    case "sm":
      return "h-6 w-6";
    case "lg":
      return "h-16 w-16";
    case "fullscreen":
      return "h-20 w-20";
    case "md":
    default:
      return "h-11 w-11";
  }
});
</script>

<template>
  <!-- Fullscreen Overlay Variant -->
  <div
    v-if="size === 'fullscreen'"
    class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-slate-900/40 p-4 backdrop-blur-md transition-all animate-fade-in"
  >
    <div class="surface-elevated flex flex-col items-center justify-center p-8 text-center shadow-2xl animate-scale-in">
      <div class="relative flex items-center justify-center" :class="sizeClass">
        <!-- Outer Glowing Orbital Ring -->
        <div class="absolute inset-0 rounded-full border-2 border-transparent border-t-brand-500 border-r-indigo-400 animate-spin"></div>
        <!-- Inner Counter-Rotating Ring -->
        <div class="absolute inset-1.5 rounded-full border-2 border-transparent border-b-cyan-400 border-l-violet-500 animate-spin-reverse"></div>
        <!-- Core Pulsing Star Dot -->
        <div class="h-3.5 w-3.5 rounded-full bg-gradient-to-tr from-brand-600 to-indigo-400 shadow-glow-sm animate-ping"></div>
        <div class="absolute h-3 w-3 rounded-full bg-brand-600"></div>
      </div>
      <p v-if="text" class="font-display mt-5 text-sm font-bold text-slate-800 dark:text-slate-100 animate-pulse">
        {{ text }}
      </p>
    </div>
  </div>

  <!-- In-page / Card Variant -->
  <div
    v-else
    class="flex flex-col items-center justify-center py-6 text-center"
    :class="showCard ? 'surface-card' : ''"
  >
    <div class="relative flex items-center justify-center" :class="sizeClass">
      <!-- Outer Rotating Orbital Gradient Ring -->
      <div
        class="absolute inset-0 rounded-full border-2 border-transparent border-t-brand-600 border-r-indigo-500 animate-spin"
      ></div>
      <!-- Inner Reverse Orbital Ring -->
      <div
        class="absolute inset-1 rounded-full border-2 border-transparent border-b-cyan-500 border-l-violet-500 animate-spin-reverse"
      ></div>
      <!-- Center Radiant Nova Core -->
      <div class="h-2.5 w-2.5 rounded-full bg-brand-600 shadow-glow-sm"></div>
    </div>

    <!-- Animated Loading Text -->
    <p
      v-if="text"
      class="font-display mt-3 text-xs font-bold text-slate-600 dark:text-slate-400"
    >
      {{ text }}
      <span class="inline-flex">
        <span class="animate-bounce-dot font-mono" style="animation-delay: 0s">.</span>
        <span class="animate-bounce-dot font-mono" style="animation-delay: 0.2s">.</span>
        <span class="animate-bounce-dot font-mono" style="animation-delay: 0.4s">.</span>
      </span>
    </p>
  </div>
</template>
