<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const router = useRouter();
const message = ref("");
const error = ref("");

const form = reactive({
  full_name: "",
  email: "",
  password: "",
});

const submit = async () => {
  message.value = "";
  error.value = "";
  try {
    await authStore.register(form);
    message.value = "Registration successful. Please login.";
    setTimeout(() => router.push({ name: "login" }), 900);
  } catch (err) {
    error.value = err.response?.data?.message || "Registration failed";
  }
};
</script>

<template>
  <div class="auth-wrap panel">
    <h2 class="section-title">Create Account</h2>
    <p class="section-subtitle">Set up your workspace in a minute.</p>
    <label>Full Name</label>
    <input v-model="form.full_name" type="text" placeholder="Your name" />
    <label>Email</label>
    <input v-model="form.email" type="email" placeholder="you@example.com" />
    <label>Password</label>
    <input v-model="form.password" type="password" placeholder="********" />
    <button style="width: 100%" @click="submit">Register</button>
    <p v-if="message" style="color: #86efac">{{ message }}</p>
    <p v-if="error" style="color: #fca5a5">{{ error }}</p>
    <p class="muted">Have an account? <router-link to="/login">Login</router-link></p>
  </div>
</template>
