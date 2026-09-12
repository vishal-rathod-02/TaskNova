<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import FormField from "../components/FormField.vue";
import { showToast } from "../composables/toast";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const router = useRouter();
const loading = ref(false);
const error = ref("");
const form = reactive({ email: "", password: "" });

const submit = async () => {
  error.value = "";
  loading.value = true;
  try {
    await authStore.login(form);
    showToast("You are signed in.");
    router.push({ name: "dashboard" });
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to sign in right now.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <main class="min-h-screen bg-paper px-4 py-10 dark:bg-night-bg sm:px-6 sm:py-16">
    <div class="mx-auto grid max-w-[960px] gap-12 lg:grid-cols-[minmax(0,1fr)_360px] lg:items-end">
      <section>
        <router-link to="/login" class="font-display text-[32px] font-semibold leading-10 text-ink dark:text-[#E7E9ED]">TaskNova</router-link>
        <h1 class="mt-16 max-w-[12ch] font-display text-5xl font-medium leading-[52px] text-ink dark:text-[#E7E9ED]">Keep a clear account of your work.</h1>
        <p class="mt-6 max-w-[55ch] text-base leading-[26px] text-slate dark:text-[#9AA3B2]">Projects, tasks, and the history behind every completed detail.</p>
      </section>
      <section class="surface border-t-4 border-t-ink p-6 dark:border-t-[#E7E9ED]">
        <h2 class="section-title">Sign in</h2>
        <p class="mt-2 body-copy">Continue to your workspace.</p>
        <form class="mt-8 grid gap-5" @submit.prevent="submit" novalidate>
          <FormField label="Email" field-id="email">
            <input id="email" v-model="form.email" class="input-field" type="email" autocomplete="email" placeholder="you@example.com" required />
          </FormField>
          <FormField label="Password" field-id="password">
            <input id="password" v-model="form.password" class="input-field" type="password" autocomplete="current-password" placeholder="Your password" required />
          </FormField>
          <p v-if="error" class="field-error" role="alert">{{ error }}</p>
          <button class="btn-primary w-full" type="submit" :disabled="loading">{{ loading ? "Signing in..." : "Sign in" }}</button>
        </form>
        <p class="mt-6 text-sm leading-5 text-slate dark:text-[#9AA3B2]">New to TaskNova? <router-link class="font-medium text-ink underline underline-offset-4 dark:text-[#E7E9ED]" to="/register">Create an account</router-link></p>
      </section>
    </div>
  </main>
</template>
