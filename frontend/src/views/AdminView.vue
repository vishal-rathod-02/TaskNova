<script setup>
import { computed, onMounted, ref } from "vue";
import AppIcon from "../components/AppIcon.vue";
import AppLoader from "../components/AppLoader.vue";
import ConfirmModal from "../components/ConfirmModal.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import SkeletonLoader from "../components/SkeletonLoader.vue";
import { showToast } from "../composables/toast";
import { useAdminStore } from "../stores/admin";
import { withMinLoading } from "../utils/async";

const adminStore = useAdminStore();
const error = ref("");
const searchQuery = ref("");
const roleFilter = ref("all");

// Modals
const isBlockModalOpen = ref(false);
const userToBlock = ref(null);
const blockLoading = ref(false);

const isDeleteModalOpen = ref(false);
const userToDelete = ref(null);
const deleteLoading = ref(false);

const users = computed(() => adminStore.users);
const loading = computed(() => adminStore.loading);

const loadUsers = async () => {
  error.value = "";
  try {
    await withMinLoading(adminStore.fetchUsers(), 1800);
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to load user accounts.";
  }
};

const filteredUsers = computed(() => {
  return users.value.filter((u) => {
    const matchesQuery =
      !searchQuery.value.trim() ||
      u.full_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      u.email.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesRole = roleFilter.value === "all" || u.role === roleFilter.value;
    return matchesQuery && matchesRole;
  });
});

const promptToggleBlock = (user) => {
  userToBlock.value = user;
  isBlockModalOpen.value = true;
};

const confirmToggleBlock = async () => {
  if (!userToBlock.value) return;
  blockLoading.value = true;
  try {
    const updated = await adminStore.toggleBlock(userToBlock.value);
    showToast(updated.is_blocked ? `Blocked ${userToBlock.value.full_name}.` : `Unblocked ${userToBlock.value.full_name}.`);
    isBlockModalOpen.value = false;
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to update access.";
  } finally {
    blockLoading.value = false;
  }
};

const promptDelete = (user) => {
  userToDelete.value = user;
  isDeleteModalOpen.value = true;
};

const confirmDelete = async () => {
  if (!userToDelete.value) return;
  deleteLoading.value = true;
  try {
    await adminStore.removeUser(userToDelete.value.id);
    showToast(`Account for "${userToDelete.value.full_name}" deleted.`);
    isDeleteModalOpen.value = false;
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to delete user.";
  } finally {
    deleteLoading.value = false;
  }
};

onMounted(loadUsers);
</script>

<template>
  <div class="page-shell">
    <PageHeader
      title="User & Student Directory"
      description="Govern student accounts, role permissions, and academic workspace policies."
      :badge="`${users.length} Registered Accounts`"
    >
      <template #actions>
        <button class="btn-secondary gap-2" type="button" :disabled="loading" @click="loadUsers">
          <AppIcon name="refresh" :size="16" :class="{ 'animate-spin': loading }" />
          {{ loading ? "Refreshing..." : "Refresh Directory" }}
        </button>
      </template>
    </PageHeader>

    <!-- Search & Filter Controls -->
    <div class="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="relative max-w-md flex-1">
        <AppIcon name="search" :size="16" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchQuery"
          type="text"
          class="input-field !mt-0 pl-10"
          placeholder="Search by student name or email..."
        />
      </div>

      <div class="flex items-center gap-2">
        <select v-model="roleFilter" class="input-field !mt-0 min-w-36 text-xs">
          <option value="all">All Roles</option>
          <option value="user">Students</option>
          <option value="admin">Administrators</option>
        </select>
      </div>
    </div>

    <!-- Error notice -->
    <p v-if="error" class="field-error mt-6" aria-live="polite">
      <AppIcon name="alert" :size="16" /> {{ error }}
    </p>

    <!-- Loading State with UIverse Skeleton & AppLoader -->
    <div v-if="loading && !users.length" class="mt-8 space-y-4">
      <SkeletonLoader type="rows" :count="5" />
      <AppLoader size="sm" text="Synchronizing student & user directory" />
    </div>

    <!-- Empty State -->
    <EmptyState
      v-else-if="!filteredUsers.length"
      class="mt-8"
      icon="users"
      title="No users match your search"
      description="Try resetting your filters to view all directory entries."
    />

    <!-- User Accounts List -->
    <section v-else class="mt-8">
      <!-- Table Header for desktop -->
      <div class="hidden grid-cols-[minmax(0,1.2fr)_150px_140px_180px] gap-4 border-b border-slate-200/80 px-4 pb-3 font-mono text-xs font-bold uppercase tracking-wider text-slate-400 md:grid dark:border-slate-800">
        <span>Account & Student</span>
        <span>Role</span>
        <span>Account Status</span>
        <span class="text-right">Actions</span>
      </div>

      <div class="mt-2 space-y-2.5">
        <article
          v-for="user in filteredUsers"
          :key="user.id"
          class="surface-card flex flex-col justify-between gap-4 p-4 transition-all duration-150 md:grid md:grid-cols-[minmax(0,1.2fr)_150px_140px_180px] md:items-center"
        >
          <!-- User Details -->
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 flex-none items-center justify-center rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 font-display text-sm font-bold text-white shadow-sm">
              {{ (user.full_name || "U").charAt(0).toUpperCase() }}
            </div>
            <div class="min-w-0">
              <h2 class="font-sans text-sm font-bold text-slate-900 dark:text-white truncate">
                {{ user.full_name }}
              </h2>
              <p class="font-mono text-xs text-slate-500 dark:text-slate-400 truncate">
                {{ user.email }}
              </p>
            </div>
          </div>

          <!-- Role -->
          <div>
            <span
              class="inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-bold"
              :class="user.role === 'admin' ? 'bg-academic-purpleLight text-academic-purple dark:bg-purple-950/60 dark:text-purple-300' : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'"
            >
              <AppIcon :name="user.role === 'admin' ? 'admin' : 'academic'" :size="12" />
              {{ user.role === 'admin' ? 'Administrator' : 'Student' }}
            </span>
          </div>

          <!-- Status -->
          <div>
            <span
              class="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold"
              :class="user.is_blocked ? 'bg-rose-50 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300' : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300'"
            >
              <span class="h-2 w-2 rounded-full" :class="user.is_blocked ? 'bg-rose-500' : 'bg-emerald-500'"></span>
              {{ user.is_blocked ? "Access Blocked" : "Active" }}
            </span>
          </div>

          <!-- Actions -->
          <div class="flex items-center justify-end gap-2">
            <template v-if="user.role !== 'admin'">
              <button
                type="button"
                class="rounded-xl border px-3 py-1 text-xs font-bold transition-all"
                :class="user.is_blocked ? 'border-emerald-300 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:border-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300' : 'border-amber-300 bg-amber-50 text-amber-700 hover:bg-amber-100 dark:border-amber-800 dark:bg-amber-950/50 dark:text-amber-300'"
                @click="promptToggleBlock(user)"
              >
                {{ user.is_blocked ? "Unblock" : "Block" }}
              </button>

              <button
                type="button"
                class="rounded-xl border border-rose-200 bg-rose-50 p-1.5 text-rose-600 hover:bg-rose-100 dark:border-rose-900/50 dark:bg-rose-950/40 dark:text-rose-400"
                title="Delete Account"
                @click="promptDelete(user)"
              >
                <AppIcon name="trash" :size="14" />
              </button>
            </template>
            <span v-else class="font-mono text-xs font-semibold text-slate-400">
              Protected Root
            </span>
          </div>
        </article>
      </div>
    </section>

    <!-- Confirm Modal for Block/Unblock -->
    <ConfirmModal
      :is-open="isBlockModalOpen"
      :title="userToBlock?.is_blocked ? 'Unblock User Account?' : 'Block User Account?'"
      :message="userToBlock?.is_blocked ? `Allow '${userToBlock?.full_name}' to access the workspace again.` : `Blocking '${userToBlock?.full_name}' will prevent them from signing in.`"
      :confirm-text="userToBlock?.is_blocked ? 'Unblock User' : 'Block User'"
      :is-danger="!userToBlock?.is_blocked"
      :loading="blockLoading"
      @cancel="isBlockModalOpen = false"
      @confirm="confirmToggleBlock"
    />

    <!-- Confirm Modal for Delete User -->
    <ConfirmModal
      :is-open="isDeleteModalOpen"
      title="Delete User Account?"
      :message="`Are you sure you want to delete the account for '${userToDelete?.full_name}'? All owned courses, tasks, and history will be deleted.`"
      confirm-text="Delete Account"
      :is-danger="true"
      :loading="deleteLoading"
      @cancel="isDeleteModalOpen = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
