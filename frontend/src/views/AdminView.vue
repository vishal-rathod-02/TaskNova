<script setup>
import { computed, onMounted, ref } from "vue";
import AppIcon from "../components/AppIcon.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import { showToast } from "../composables/toast";
import { useAdminStore } from "../stores/admin";

const adminStore = useAdminStore();
const error = ref("");
const users = computed(() => adminStore.users);
const loading = computed(() => adminStore.loading);

const loadUsers = async () => {
  error.value = "";
  try {
    await adminStore.fetchUsers();
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to load user accounts.";
  }
};

const toggleBlock = async (user) => {
  error.value = "";
  try {
    const updated = await adminStore.toggleBlock(user);
    showToast(updated.is_blocked ? "User blocked." : "User unblocked.");
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to update user access.";
  }
};

const removeUser = async (user) => {
  if (!window.confirm(`Delete the account for "${user.full_name}"? This cannot be undone.`)) return;
  error.value = "";
  try {
    await adminStore.removeUser(user.id);
    showToast("User deleted.");
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to delete user.";
  }
};

onMounted(loadUsers);
</script>

<template>
  <div class="page-shell">
    <PageHeader title="User management" description="Review account access and enforce workspace policy.">
      <template #actions>
        <button class="btn-secondary gap-2" type="button" :disabled="loading" @click="loadUsers"><AppIcon name="refresh" :size="16" />{{ loading ? "Refreshing..." : "Refresh" }}</button>
      </template>
    </PageHeader>
    <p v-if="error" class="field-error mt-6" aria-live="polite">{{ error }}</p>
    <p v-if="loading" class="mt-10 text-sm text-slate dark:text-[#9AA3B2]">Loading user accounts...</p>
    <EmptyState v-else-if="!users.length" class="mt-10" title="No users found" />
    <section v-else class="mt-10">
      <div class="hidden grid-cols-[minmax(0,1fr)_130px_130px_190px] gap-5 border-b border-slate/20 pb-3 md:grid dark:border-slate/30"><span class="data-label">Account</span><span class="data-label">Role</span><span class="data-label">Status</span><span class="data-label text-right">Actions</span></div>
      <div class="border-t border-slate/20 md:border-t-0 dark:border-slate/30">
        <article v-for="user in users" :key="user.id" class="ledger-row md:grid-cols-[minmax(0,1fr)_130px_130px_190px]">
          <div class="min-w-0"><h2 class="truncate text-base font-medium text-ink dark:text-[#E7E9ED]">{{ user.full_name }}</h2><p class="mt-1 data-label">{{ user.email }}</p></div>
          <span class="text-sm text-ink dark:text-[#E7E9ED]">{{ user.role }}</span>
          <span :class="user.is_blocked ? 'text-ember dark:text-ember-dark' : 'text-ledger-green dark:text-ledger-greenDark'" class="text-sm font-medium">{{ user.is_blocked ? "Blocked" : "Active" }}</span>
          <div class="flex flex-wrap gap-x-3 gap-y-1 md:justify-end"><button v-if="user.role !== 'admin'" class="min-h-11 px-1 text-sm font-medium text-ink underline decoration-slate/50 underline-offset-4 hover:decoration-ink dark:text-[#E7E9ED]" type="button" @click="toggleBlock(user)">{{ user.is_blocked ? "Unblock" : "Block" }}</button><button v-if="user.role !== 'admin'" class="btn-danger" type="button" @click="removeUser(user)">Delete user</button></div>
        </article>
      </div>
    </section>
  </div>
</template>
