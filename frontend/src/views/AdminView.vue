<script setup>
import { computed, onMounted, ref } from "vue";
import AppIcon from "../components/AppIcon.vue";
import ConfirmModal from "../components/ConfirmModal.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import SkeletonLoader from "../components/SkeletonLoader.vue";
import { showToast } from "../composables/toast";
import { getAdminDashboard } from "../services/analytics";
import { useAdminStore } from "../stores/admin";
import { useAuthStore } from "../stores/auth";
import { withMinLoading } from "../utils/async";

const adminStore = useAdminStore();
const authStore = useAuthStore();
const error = ref("");
const searchQuery = ref("");
const roleFilter = ref("all");
const sysStats = ref(null);
const sysLoading = ref(false);

// Modals
const isBlockModalOpen = ref(false);
const userToBlock = ref(null);
const blockLoading = ref(false);

const isDeleteModalOpen = ref(false);
const userToDelete = ref(null);
const deleteLoading = ref(false);

const users = computed(() => adminStore.users);
const loading = computed(() => adminStore.loading);
const memberCount = computed(() => users.value.filter((u) => u.role !== "admin").length);
const adminCount = computed(() => users.value.filter((u) => u.role === "admin").length);

const loadUsers = async () => {
  error.value = "";
  try {
    await withMinLoading(adminStore.fetchUsers(), 1800);
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to load user accounts.";
  }
};

const loadSysStats = async () => {
  sysLoading.value = true;
  try {
    const { data } = await getAdminDashboard();
    sysStats.value = data.stats;
  } catch {
    sysStats.value = null;
  } finally {
    sysLoading.value = false;
  }
};

const templates = computed(() => adminStore.templates);
const templatesLoading = computed(() => adminStore.templatesLoading);
const togglingTemplate = ref("");

const loadTemplates = async () => {
  try {
    await adminStore.fetchRoutineTemplates();
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to load routine templates.";
  }
};

const handleToggleTemplate = async (template) => {
  togglingTemplate.value = template.name;
  try {
    const updated = await adminStore.toggleRoutineTemplate(template);
    showToast(updated.is_enabled ? `Enabled the ${template.label} template.` : `Disabled the ${template.label} template.`, updated.is_enabled ? "success" : "info");
  } catch (requestError) {
    error.value = requestError.response?.data?.message || "Unable to update template.";
  } finally {
    togglingTemplate.value = "";
  }
};

const sysCompletionRate = computed(() => {
  const total = sysStats.value?.total_tasks || 0;
  if (!total) return 0;
  return Math.round(((sysStats.value?.completed_tasks || 0) / total) * 100);
});

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

onMounted(() => {
  loadUsers();
  loadSysStats();
  loadTemplates();
});
</script>

<template>
  <div class="page-shell">
    <PageHeader
      title="Platform Governor Console"
      description="Monitor growth, routine adoption, and member access across the hub."
      :badge="`${memberCount} Members · ${adminCount} Admins`"
    >
      <template #actions>
        <button class="btn-secondary gap-2" type="button" :disabled="loading" @click="loadUsers">
          <AppIcon name="refresh" :size="16" :class="{ 'animate-spin': loading }" />
          {{ loading ? "Refreshing..." : "Refresh Directory" }}
        </button>
      </template>
    </PageHeader>

    <!-- System Health Overview (live from /api/analytics/admin) -->
    <section aria-label="System health overview" class="mt-8">
      <div v-if="sysLoading && !sysStats" class="grid grid-cols-2 gap-2.5 lg:grid-cols-3">
        <div v-for="i in 6" :key="i" class="metric-card shimmer-skeleton min-h-24"></div>
      </div>
      <div v-else-if="sysStats" class="grid grid-cols-2 gap-2.5 lg:grid-cols-3">
        <div class="metric-card p-4">
          <p class="data-label">Registered Members</p>
          <p class="metric-value mt-1 text-2xl sm:text-3xl">{{ sysStats.total_members ?? sysStats.total_users }}</p>
          <p class="mt-1 font-mono text-[11px] text-slate-500 dark:text-slate-400">{{ sysStats.active_members ?? sysStats.active_users }} active · {{ sysStats.blocked_members ?? sysStats.blocked_users }} blocked</p>
          <p class="mt-0.5 font-mono text-[11px] font-bold text-brand-600 dark:text-brand-400">{{ sysStats.total_admins ?? 0 }} platform admins</p>
        </div>
        <div class="metric-card p-4">
          <p class="data-label">Projects</p>
          <p class="metric-value mt-1 text-2xl sm:text-3xl">{{ sysStats.total_projects }}</p>
          <p class="mt-1 font-mono text-[11px] text-slate-500 dark:text-slate-400">across workspace</p>
        </div>
        <div class="metric-card p-4">
          <p class="data-label">Task Workload</p>
          <p class="metric-value mt-1 text-2xl sm:text-3xl">{{ sysStats.total_tasks }}</p>
          <p class="mt-1 font-mono text-[11px] text-slate-500 dark:text-slate-400">{{ sysStats.completed_tasks }} done ({{ sysCompletionRate }}%)</p>
        </div>
        <div class="metric-card p-4" :class="{ 'border-rose-200 dark:border-rose-900/50': sysStats.overdue_tasks > 0 }">
          <p class="data-label" :class="{ 'text-rose-600 dark:text-rose-400': sysStats.overdue_tasks > 0 }">Overdue Tasks</p>
          <p class="metric-value mt-1 text-2xl sm:text-3xl" :class="{ 'text-rose-600 dark:text-rose-400': sysStats.overdue_tasks > 0 }">{{ sysStats.overdue_tasks }}</p>
          <p class="mt-1 font-mono text-[11px] text-slate-500 dark:text-slate-400">{{ sysStats.overdue_tasks > 0 ? "needs attention" : "all clear" }}</p>
        </div>
        <div class="metric-card p-4">
          <p class="data-label">Activity · 24h</p>
          <p class="metric-value mt-1 text-2xl sm:text-3xl">{{ sysStats.activity_last_24h }}</p>
          <p class="mt-1 font-mono text-[11px] text-slate-500 dark:text-slate-400">task events logged</p>
        </div>
        <div class="metric-card flex flex-col justify-center p-4">
          <p class="data-label">Workspace Completion</p>
          <div class="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full bg-gradient-to-r from-brand-500 to-emerald-500 transition-all duration-500" :style="{ width: `${sysCompletionRate}%` }"></div>
          </div>
          <p class="mt-1.5 font-mono text-[11px] font-bold text-slate-600 dark:text-slate-300">{{ sysCompletionRate }}% of all tasks done</p>
        </div>
      </div>
    </section>

    <!-- Growth & Routine Adoption (Trajectory 2: is the hub story landing?) -->
    <section aria-label="Growth and routine adoption" class="mt-8">
      <h2 class="font-display text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Growth & Routine Adoption</h2>
      <div v-if="sysLoading && !sysStats" class="mt-3 grid grid-cols-2 gap-2.5 lg:grid-cols-4">
        <div v-for="i in 4" :key="i" class="metric-card shimmer-skeleton min-h-24"></div>
      </div>
      <div v-else-if="sysStats" class="mt-3 grid grid-cols-2 gap-2.5 lg:grid-cols-4">
        <div class="metric-card p-4">
          <p class="data-label">New Members · 7d</p>
          <p class="metric-value mt-1 text-2xl sm:text-3xl">{{ sysStats.signups_7d }}</p>
          <p class="mt-1 font-mono text-[11px] text-slate-500 dark:text-slate-400">{{ sysStats.signups_30d }} in last 30 days</p>
        </div>
        <div class="metric-card p-4">
          <p class="data-label">Weekly Active</p>
          <p class="metric-value mt-1 text-2xl sm:text-3xl">{{ sysStats.weekly_active_users }}</p>
          <p class="mt-1 font-mono text-[11px] text-slate-500 dark:text-slate-400">logged activity in 7 days</p>
        </div>
        <div class="metric-card flex flex-col justify-center p-4">
          <p class="data-label">Activated Members</p>
          <p class="metric-value mt-1 text-2xl sm:text-3xl">{{ sysStats.activated_members }}</p>
          <div class="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full bg-gradient-to-r from-brand-500 to-cyan-500 transition-all duration-500" :style="{ width: `${sysStats.activation_rate}%` }"></div>
          </div>
          <p class="mt-1.5 font-mono text-[11px] font-bold text-slate-600 dark:text-slate-300">{{ sysStats.activation_rate }}% own a project</p>
        </div>
        <div class="metric-card flex flex-col justify-center p-4">
          <p class="data-label">Routine Adopters</p>
          <p class="metric-value mt-1 text-2xl sm:text-3xl">{{ sysStats.routine_adopters }}</p>
          <div class="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <div class="h-full rounded-full bg-gradient-to-r from-violet-500 to-brand-500 transition-all duration-500" :style="{ width: `${sysStats.routine_adoption_rate}%` }"></div>
          </div>
          <p class="mt-1.5 font-mono text-[11px] font-bold text-slate-600 dark:text-slate-300">
            {{ sysStats.routine_adoption_rate }}% · {{ sysStats.total_routine_slots }} blocks · {{ sysStats.total_allocations }} auto-slotted
          </p>
        </div>
      </div>
      <p v-if="sysStats?.slot_type_mix?.length" class="mt-2.5 font-mono text-[11px] text-slate-500 dark:text-slate-400">
        Block mix: {{ sysStats.slot_type_mix.map((m) => `${m.label} ×${m.count}`).join(" · ") }}
      </p>
    </section>

    <!-- Routine Template Governance (publish which starters members can apply) -->
    <section aria-label="Routine template governance" class="mt-8">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <h2 class="font-display text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Starter Templates</h2>
        <button class="btn-secondary gap-2 !py-1.5 text-xs" type="button" :disabled="templatesLoading" @click="loadTemplates">
          <AppIcon name="refresh" :size="14" :class="{ 'animate-spin': templatesLoading }" />
          Refresh
        </button>
      </div>
      <div v-if="templatesLoading && !templates.length" class="mt-3 grid gap-2.5 sm:grid-cols-2">
        <div v-for="i in 4" :key="i" class="metric-card shimmer-skeleton min-h-24"></div>
      </div>
      <div v-else class="mt-3 grid gap-2.5 sm:grid-cols-2">
        <article
          v-for="template in templates"
          :key="template.name"
          class="surface-card flex items-start justify-between gap-3 p-4"
          :class="{ 'opacity-70': !template.is_enabled }"
        >
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <h3 class="font-display text-sm font-bold text-slate-900 dark:text-white">{{ template.label }}</h3>
              <span
                class="rounded-full px-2 py-0.5 font-mono text-[10px] font-bold"
                :class="template.is_enabled ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'"
              >
                {{ template.is_enabled ? "Live" : "Disabled" }}
              </span>
            </div>
            <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ template.description }}</p>
            <p class="mt-1.5 font-mono text-[11px] text-slate-500 dark:text-slate-400">
              {{ template.blocks_per_week }} blocks/week · {{ template.active_blocks }} live · {{ template.adopters }} adopters
            </p>
          </div>
          <button
            type="button"
            role="switch"
            :aria-checked="template.is_enabled"
            :aria-label="`Toggle ${template.label}`"
            :disabled="togglingTemplate === template.name"
            class="relative h-6 w-11 flex-none rounded-full transition-colors"
            :class="template.is_enabled ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-slate-700'"
            @click="handleToggleTemplate(template)"
          >
            <span
              class="absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-all"
              :class="template.is_enabled ? 'left-[22px]' : 'left-0.5'"
            ></span>
          </button>
        </article>
      </div>
    </section>

    <!-- Search & Filter Controls -->
    <div class="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="relative max-w-md flex-1">
        <AppIcon name="search" :size="16" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchQuery"
          type="text"
          class="input-field !mt-0 pl-10"
          placeholder="Search by name or email..."
        />
      </div>

      <div class="flex items-center gap-2">
        <select v-model="roleFilter" class="input-field !mt-0 min-w-36 text-xs">
          <option value="all">All Roles</option>
          <option value="user">Standard</option>
          <option value="admin">Administrators</option>
        </select>
      </div>
    </div>

    <!-- Error notice -->
    <p v-if="error" class="field-error mt-6" aria-live="polite">
      <AppIcon name="alert" :size="16" /> {{ error }}
    </p>

    <!-- Loading State with Skeleton only (no spinner to avoid double-loader flash) -->
    <div v-if="loading && !users.length" class="mt-8 space-y-4">
      <SkeletonLoader type="rows" :count="5" />
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
        <span>Account & Member</span>
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
              {{ user.role === 'admin' ? 'Administrator' : 'Member' }}
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
            <template v-if="user.id !== authStore.user?.id">
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
            <span v-else class="rounded-lg bg-brand-50 dark:bg-brand-950/60 px-2.5 py-1 font-mono text-[11px] font-bold text-brand-600 dark:text-brand-400 border border-brand-200 dark:border-brand-900">
              You (Active)
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
      :message="`Are you sure you want to delete the account for '${userToDelete?.full_name}'? All owned projects, tasks, routines, and history will be deleted.`"
      confirm-text="Delete Account"
      :is-danger="true"
      :loading="deleteLoading"
      @cancel="isDeleteModalOpen = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
