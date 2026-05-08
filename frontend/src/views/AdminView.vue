<script setup>
import { onMounted, ref } from "vue";
import apiClient from "../api/client";

const users = ref([]);
const loading = ref(false);
const error = ref("");

const loadUsers = async () => {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await apiClient.get("/admin/users");
    users.value = data.users;
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to load users";
  } finally {
    loading.value = false;
  }
};

const toggleBlock = async (id) => {
  await apiClient.post(`/admin/users/${id}/toggle-block`);
  await loadUsers();
};

const removeUser = async (id) => {
  await apiClient.delete(`/admin/users/${id}`);
  await loadUsers();
};

onMounted(loadUsers);
</script>

<template>
  <section class="panel">
    <div class="title-row">
      <div>
        <h3 class="section-title">Admin User Management</h3>
        <p class="section-subtitle">Review user access and enforce account policies.</p>
      </div>
      <button class="secondary" @click="loadUsers">Refresh</button>
    </div>
    <p v-if="error" style="color: #fca5a5">{{ error }}</p>
    <p v-if="loading" class="empty-state">Loading users...</p>
    <div v-else-if="!users.length" class="empty-state">No users found.</div>
    <div v-for="user in users" :key="user.id" class="task-row">
      <div>
        <strong style="font-size: 15px">{{ user.full_name }}</strong>
        <p class="muted" style="margin: 4px 0 8px">{{ user.email }}</p>
        <span class="chip">{{ user.role }}</span>
        <span v-if="user.is_blocked" class="chip warn" style="margin-left: 8px">Blocked</span>
      </div>
      <div class="inline-actions">
        <button class="secondary" @click="toggleBlock(user.id)">
          {{ user.is_blocked ? "Unblock" : "Block" }}
        </button>
        <button v-if="user.role !== 'admin'" class="danger" @click="removeUser(user.id)">Delete</button>
      </div>
    </div>
  </section>
</template>
