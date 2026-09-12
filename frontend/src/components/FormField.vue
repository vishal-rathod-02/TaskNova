<script setup>
import { computed } from "vue";

const props = defineProps({
  label: { type: String, required: true },
  fieldId: { type: String, required: true },
  help: { type: String, default: "" },
  error: { type: String, default: "" },
});

const describedBy = computed(() => {
  const ids = [];
  if (props.help) ids.push(`${props.fieldId}-help`);
  if (props.error) ids.push(`${props.fieldId}-error`);
  return ids.join(" ") || undefined;
});
</script>

<template>
  <label class="field-label" :for="fieldId">
    {{ label }}
    <slot :described-by="describedBy" :invalid="!!error" />
    <span v-if="help && !error" :id="`${fieldId}-help`" class="field-help">{{ help }}</span>
    <span v-if="error" :id="`${fieldId}-error`" class="field-error" role="alert">{{ error }}</span>
  </label>
</template>
