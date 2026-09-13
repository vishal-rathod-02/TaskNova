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
const form = reactive({ email: "", password: "" });

const submit = async () => {
  error.value = "";
  loading.value = true;
  try {
    await authStore.login(form);
    showToast("Signed in successfully. Welcome back!");
    router.push({ name: "dashboard" });
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to sign in. Please verify credentials.";
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
          Keep a clear, focused ledger of your academic work.
        </h1>

        <p class="body-copy max-w-lg text-base">
          From multi-week capstone projects to weekly lab assignments, TaskNova keeps deadlines, course history, and study momentum in one elevated workspace.
        </p>

        <!-- Feature List -->
        <div class="grid gap-3 pt-2 sm:grid-cols-2">
          <div class="flex items-center gap-2.5 text-xs font-semibold text-slate-700 dark:text-slate-300">
            <div class="flex h-6 w-6 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
              <AppIcon name="check" :size="14" />
            </div>
            <span>Course & Syllabus Ledgers</span>
          </div>
          <div class="flex items-center gap-2.5 text-xs font-semibold text-slate-700 dark:text-slate-300">
            <div class="flex h-6 w-6 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
              <AppIcon name="check" :size="14" />
            </div>
            <span>Interactive Kanban & List views</span>
          </div>
          <div class="flex items-center gap-2.5 text-xs font-semibold text-slate-700 dark:text-slate-300">
            <div class="flex h-6 w-6 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
              <AppIcon name="check" :size="14" />
            </div>
            <span>Pomodoro Focus Study Timer</span>
          </div>
          <div class="flex items-center gap-2.5 text-xs font-semibold text-slate-700 dark:text-slate-300">
            <div class="flex h-6 w-6 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
              <AppIcon name="check" :size="14" />
            </div>
            <span>Automated Deadline Warnings</span>
          </div>
        </div>
      </section>

      <!-- Right Sign In Panel -->
      <section class="lg:col-span-5">
        <div class="surface-elevated p-8">
          <h2 class="font-display text-2xl font-bold text-slate-900 dark:text-white">Sign In</h2>
          <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">Enter your credentials to enter your academic workspace.</p>

          <form class="mt-6 space-y-4" @submit.prevent="submit" novalidate>
            <FormField label="Email Address" field-id="email">
              <input
                id="email"
                v-model="form.email"
                class="input-field"
                type="email"
                autocomplete="email"
                placeholder="student@university.edu"
                required
              />
            </FormField>

            <FormField label="Password" field-id="password">
              <input
                id="password"
                v-model="form.password"
                class="input-field"
                type="password"
                autocomplete="current-password"
                placeholder="Enter your password"
                required
              />
            </FormField>

            <p v-if="error" class="field-error" role="alert">
              <AppIcon name="alert" :size="14" /> {{ error }}
            </p>

            <button class="btn-primary w-full mt-2" type="submit" :disabled="loading">
              <span v-if="loading" class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
              {{ loading ? "Signing in..." : "Sign In to Workspace" }}
            </button>
          </form>

          <div class="mt-6 border-t border-slate-100 pt-4 text-center text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">
            <span>New to TaskNova?</span>
            <router-link class="font-bold text-brand-600 hover:underline dark:text-brand-400 ml-1" to="/register">
              Create an account
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
