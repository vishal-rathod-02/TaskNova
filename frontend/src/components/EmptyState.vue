<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: "" },
});
</script>

<template>
  <div class="border-y border-slate/20 py-10 dark:border-slate/30">
    <h2 class="section-title">{{ title }}</h2>
    <p v-if="description" class="mt-2 body-copy">{{ description }}</p>
    <div v-if="$slots.actions" class="mt-6 flex flex-wrap gap-3">
      <slot name="actions" />
    </div>
  </div>
</template>
