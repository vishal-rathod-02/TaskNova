<script setup>
import { onErrorCaptured, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const error = ref(null);

onErrorCaptured((viewError) => {
  error.value = viewError;
  return false;
});

const reset = () => {
  error.value = null;
  router.push({ name: "dashboard" });
};
</script>

<template>
  <div v-if="error" class="page-shell">
    <p class="data-label">Something broke</p>
    <h1 class="page-title mt-2">This view ran into a problem.</h1>
    <p class="mt-2 body-copy">The rest of your ledger is safe. Return to the dashboard and try again.</p>
    <button class="btn-primary mt-6" type="button" @click="reset">Back to dashboard</button>
  </div>
  <slot v-else />
</template>
