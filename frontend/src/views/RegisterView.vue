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
const formErrors = ref({});
const form = reactive({ full_name: "", email: "", password: "" });

const submit = async () => {
  error.value = "";
  formErrors.value = {};
  loading.value = true;
  try {
    await authStore.register(form);
    showToast("Account created. Sign in to begin.");
    router.push({ name: "login" });
  } catch (requestError) {
    formErrors.value = requestError.response?.data?.errors || {};
    error.value = requestError.response?.data?.message || "Unable to create your account.";
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
        <h1 class="mt-16 max-w-[12ch] font-display text-5xl font-medium leading-[52px] text-ink dark:text-[#E7E9ED]">Start with one project and move it forward.</h1>
        <p class="mt-6 max-w-[55ch] text-base leading-[26px] text-slate dark:text-[#9AA3B2]">Your workspace keeps the work, the due dates, and the record of progress in one considered place.</p>
      </section>
      <section class="surface border-t-4 border-t-ink p-6 dark:border-t-[#E7E9ED]">
        <h2 class="section-title">Create account</h2>
        <p class="mt-2 body-copy">It takes less than a minute.</p>
        <form class="mt-8 grid gap-5" @submit.prevent="submit" novalidate>
          <FormField label="Full name" field-id="full-name" :error="formErrors.full_name || ''">
            <input id="full-name" v-model="form.full_name" class="input-field" type="text" autocomplete="name" maxlength="120" placeholder="Your name" required :aria-invalid="!!formErrors.full_name" />
          </FormField>
          <FormField label="Email" field-id="register-email" :error="formErrors.email || ''">
            <input id="register-email" v-model="form.email" class="input-field" type="email" autocomplete="email" placeholder="you@example.com" required :aria-invalid="!!formErrors.email" />
          </FormField>
          <FormField label="Password" field-id="register-password" help="Use at least 8 characters." :error="formErrors.password || ''">
            <input id="register-password" v-model="form.password" class="input-field" type="password" autocomplete="new-password" minlength="8" placeholder="At least 8 characters" required :aria-invalid="!!formErrors.password" />
          </FormField>
          <p v-if="error && !Object.keys(formErrors).length" class="field-error" role="alert">{{ error }}</p>
          <button class="btn-primary w-full" type="submit" :disabled="loading">{{ loading ? "Creating account..." : "Create account" }}</button>
        </form>
        <p class="mt-6 text-sm leading-5 text-slate dark:text-[#9AA3B2]">Already have an account? <router-link class="font-medium text-ink underline underline-offset-4 dark:text-[#E7E9ED]" to="/login">Sign in</router-link></p>
      </section>
    </div>
  </main>
</template>
