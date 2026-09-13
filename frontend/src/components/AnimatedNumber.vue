<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  value: { type: Number, default: 0 },
  duration: { type: Number, default: 900 },
  prefix: { type: String, default: "" },
  suffix: { type: String, default: "" },
  decimals: { type: Number, default: 0 },
  useGrouping: { type: Boolean, default: true },
});

const displayedNumber = ref(0);
let animationFrameId = null;
let startTimestamp = null;
let startVal = 0;
let endVal = 0;

// Cubic easing out: smooth decelerating motion
const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

const animate = (timestamp) => {
  if (!startTimestamp) startTimestamp = timestamp;
  const elapsed = timestamp - startTimestamp;
  const progress = Math.min(elapsed / props.duration, 1);
  const eased = easeOutCubic(progress);

  displayedNumber.value = startVal + (endVal - startVal) * eased;

  if (progress < 1) {
    animationFrameId = requestAnimationFrame(animate);
  } else {
    displayedNumber.value = endVal;
  }
};

const startAnimation = (newVal, oldVal = 0) => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  startVal = typeof oldVal === "number" && !isNaN(oldVal) ? oldVal : 0;
  endVal = typeof newVal === "number" && !isNaN(newVal) ? newVal : 0;
  startTimestamp = null;
  animationFrameId = requestAnimationFrame(animate);
};

watch(
  () => props.value,
  (newVal, oldVal) => {
    startAnimation(newVal, oldVal ?? 0);
  }
);

onMounted(() => {
  startAnimation(props.value, 0);
});

onBeforeUnmount(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
});

const formattedNumber = computed(() => {
  const num = displayedNumber.value;
  if (isNaN(num)) return `${props.prefix}0${props.suffix}`;

  const fixed = num.toFixed(props.decimals);
  if (!props.useGrouping) {
    return `${props.prefix}${fixed}${props.suffix}`;
  }

  const parts = fixed.split(".");
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return `${props.prefix}${parts.join(".")}${props.suffix}`;
});
</script>

<template>
  <span class="inline-block tabular-nums transition-transform duration-200">
    {{ formattedNumber }}
  </span>
</template>
