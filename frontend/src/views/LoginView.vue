<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const router = useRouter();
const error = ref("");

const form = reactive({
  email: "",
  password: "",
});

const submit = async () => {
  error.value = "";
  try {
    await authStore.login(form);
    router.push({ name: "dashboard" });
  } catch (err) {
    error.value = err.response?.data?.message || "Login failed";
  }
};
</script>

<template>
  <div class="auth-wrap panel">
    <h2 class="section-title">Welcome Back</h2>
    <p class="section-subtitle">Sign in to your TaskNova workspace.</p>
    <label>Email</label>
    <input v-model="form.email" type="email" placeholder="you@example.com" />
    <label>Password</label>
    <input v-model="form.password" type="password" placeholder="********" />
    <button style="width: 100%" @click="submit">Login</button>
    <p v-if="error" style="color: #fca5a5">{{ error }}</p>
    <p class="muted">New user? <router-link to="/register">Create account</router-link></p>
  </div>
</template>
