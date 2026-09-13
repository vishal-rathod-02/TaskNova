<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import AppIcon from "../components/AppIcon.vue";
import BrandLogo from "../components/BrandLogo.vue";
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
    showToast("Account created successfully. Sign in to start your workspace.");
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
  <main class="min-h-screen bg-paper px-4 py-8 dark:bg-night-bg sm:px-6 lg:flex lg:items-center lg:justify-center">
    <div class="mx-auto grid w-full max-w-5xl gap-10 lg:grid-cols-12 lg:items-center">
      <!-- Left Hero Section -->
      <section class="lg:col-span-7 space-y-6">
        <BrandLogo size="lg" to="/login" />

        <h1 class="font-display text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-tight">
          Structure your academic journey with precision.
        </h1>

        <p class="body-copy max-w-lg text-base">
          Start with a single course or research project and build a reliable rhythm of accountability, progress, and achievement.
        </p>

        <!-- Perks Card -->
        <div class="rounded-2xl border border-slate-200/80 bg-white/60 p-5 backdrop-blur-sm dark:border-slate-800 dark:bg-night-card/60">
          <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400">
            <AppIcon name="sparkles" :size="16" />
            <span>Included for Students</span>
          </div>
          <p class="mt-2 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
            Unlimited courses, interactive Kanban boards, personal productivity digests, and Pomodoro study sprints designed specifically for students.
          </p>
        </div>
      </section>

      <!-- Right Registration Form Panel -->
      <section class="lg:col-span-5">
        <div class="surface-elevated p-8">
          <h2 class="font-display text-2xl font-bold text-slate-900 dark:text-white">Create Account</h2>
          <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">Get your personal academic workspace ready in under a minute.</p>

          <form class="mt-6 space-y-4" @submit.prevent="submit" novalidate>
            <FormField label="Full Name" field-id="full-name" :error="formErrors.full_name || ''">
              <input
                id="full-name"
                v-model="form.full_name"
                class="input-field"
                type="text"
                autocomplete="name"
                maxlength="120"
                placeholder="Alex Morgan"
                required
                :aria-invalid="!!formErrors.full_name"
              />
            </FormField>

            <FormField label="University / Academic Email" field-id="register-email" :error="formErrors.email || ''">
              <input
                id="register-email"
                v-model="form.email"
                class="input-field"
                type="email"
                autocomplete="email"
                placeholder="alex@university.edu"
                required
                :aria-invalid="!!formErrors.email"
              />
            </FormField>

            <FormField label="Password" field-id="register-password" help="Use at least 8 characters." :error="formErrors.password || ''">
              <input
                id="register-password"
                v-model="form.password"
                class="input-field"
                type="password"
                autocomplete="new-password"
                minlength="8"
                placeholder="At least 8 characters"
                required
                :aria-invalid="!!formErrors.password"
              />
            </FormField>

            <p v-if="error && !Object.keys(formErrors).length" class="field-error" role="alert">
              <AppIcon name="alert" :size="14" /> {{ error }}
            </p>

            <button class="btn-primary w-full mt-2" type="submit" :disabled="loading">
              <span v-if="loading" class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
              {{ loading ? "Creating Workspace..." : "Create Free Account" }}
            </button>
          </form>

          <div class="mt-6 border-t border-slate-100 pt-4 text-center text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">
            <span>Already have an account?</span>
            <router-link class="font-bold text-brand-600 hover:underline dark:text-brand-400 ml-1" to="/login">
              Sign in
            </router-link>
            <div class="mt-3 flex items-center justify-center gap-2 text-[11px] font-mono text-slate-400 dark:text-slate-500">
              <span>TaskNova Academic</span>
              <span>•</span>
              <span class="rounded bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 font-bold text-slate-600 dark:text-slate-400">v1.0</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>
