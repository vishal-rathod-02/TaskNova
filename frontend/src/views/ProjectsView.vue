<script setup>
import { computed, onMounted, ref } from "vue";
import AppIcon from "../components/AppIcon.vue";
import AppLoader from "../components/AppLoader.vue";
import ConfirmModal from "../components/ConfirmModal.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import ProjectModal from "../components/ProjectModal.vue";
import SkeletonLoader from "../components/SkeletonLoader.vue";
import TaskModal from "../components/TaskModal.vue";
import { showToast } from "../composables/toast";
import { useProjectStore } from "../stores/projects";
import { useTaskStore } from "../stores/tasks";
import { withMinLoading } from "../utils/async";

const projectStore = useProjectStore();
const taskStore = useTaskStore();

const searchQuery = ref("");
const error = ref("");
const formErrors = ref({});
const modalLoading = ref(false);

// Modals
const isProjectModalOpen = ref(false);
const isEditMode = ref(false);
const selectedProject = ref(null);

const isDeleteModalOpen = ref(false);
const projectToDelete = ref(null);
const deleteLoading = ref(false);

const isTaskModalOpen = ref(false);
const taskModalProject = ref(null);
const taskFormErrors = ref({});
const taskLoading = ref(false);

const requestMessage = (requestError, fallback) => {
  formErrors.value = requestError.response?.data?.errors || {};
  return requestError.response?.data?.message || fallback;
};

const loadProjects = async () => {
  error.value = "";
  try {
    await withMinLoading(projectStore.fetchProjects(), 1800);
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to load courses & projects.");
  }
};

const filteredProjects = computed(() => {
  if (!searchQuery.value.trim()) return projectStore.items;
  const q = searchQuery.value.toLowerCase();
  return projectStore.items.filter(
    (p) => p.name.toLowerCase().includes(q) || (p.description && p.description.toLowerCase().includes(q))
  );
});

const openCreateModal = () => {
  isEditMode.value = false;
  selectedProject.value = null;
  formErrors.value = {};
  isProjectModalOpen.value = true;
};

const openEditModal = (project) => {
  isEditMode.value = true;
  selectedProject.value = project;
  formErrors.value = {};
  isProjectModalOpen.value = true;
};

const handleSaveProject = async (formData) => {
  modalLoading.value = true;
  formErrors.value = {};
  try {
    if (isEditMode.value && selectedProject.value) {
      await projectStore.updateProject(selectedProject.value.id, formData);
      showToast("Course / Project updated successfully.");
    } else {
      await projectStore.createProject(formData);
      showToast("New Course / Project created.");
    }
    isProjectModalOpen.value = false;
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to save project.");
  } finally {
    modalLoading.value = false;
  }
};

const promptDelete = (project) => {
  projectToDelete.value = project;
  isDeleteModalOpen.value = true;
};

const confirmDelete = async () => {
  if (!projectToDelete.value) return;
  deleteLoading.value = true;
  try {
    await projectStore.deleteProject(projectToDelete.value.id);
    showToast(`Deleted "${projectToDelete.value.name}" and associated tasks.`);
    isDeleteModalOpen.value = false;
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to delete project.");
  } finally {
    deleteLoading.value = false;
  }
};

const openAddTaskModal = (project) => {
  taskModalProject.value = project;
  taskFormErrors.value = {};
  isTaskModalOpen.value = true;
};

const handleCreateTask = async (formData) => {
  taskLoading.value = true;
  taskFormErrors.value = {};
  try {
    const toUtcIso = (localInput) => (localInput ? new Date(localInput).toISOString() : null);
    await taskStore.createTask({
      ...formData,
      project_id: Number(formData.project_id),
      due_date: toUtcIso(formData.due_date),
    });
    isTaskModalOpen.value = false;
    showToast("Task added to course.");
    await projectStore.fetchProjects();
  } catch (err) {
    taskFormErrors.value = err.response?.data?.errors || {};
    error.value = err.response?.data?.message || "Unable to create task.";
  } finally {
    taskLoading.value = false;
  }
};

onMounted(loadProjects);
</script>

<template>
  <div class="page-shell">
    <PageHeader
      title="Courses & Academic Projects"
      description="Organize your curriculum, group research projects, and subject assignments into distinct ledgers."
      :badge="`${projectStore.items.length} Active`"
    >
      <template #actions>
        <button class="btn-primary gap-2" type="button" @click="openCreateModal">
          <AppIcon name="plus" :size="16" /> New Course / Project
        </button>
      </template>
    </PageHeader>

    <!-- Search and Controls Bar -->
    <div class="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="relative max-w-md flex-1">
        <AppIcon
          name="search"
          :size="16"
          class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
        />
        <input
          v-model="searchQuery"
          type="text"
          class="input-field !mt-0 pl-10"
          placeholder="Search courses or projects..."
        />
      </div>

      <button
        class="btn-secondary gap-2"
        type="button"
        :disabled="projectStore.loading"
        @click="loadProjects"
      >
        <AppIcon name="refresh" :size="16" :class="{ 'animate-spin': projectStore.loading }" />
        {{ projectStore.loading ? "Refreshing..." : "Refresh" }}
      </button>
    </div>

    <!-- Error Alert -->
    <p v-if="error" class="field-error mt-6" aria-live="polite">
      <AppIcon name="alert" :size="16" /> {{ error }}
    </p>

    <!-- Loading State with UIverse Skeleton & Orbital AppLoader -->
    <div v-if="projectStore.loading && !projectStore.items.length" class="mt-8 space-y-6">
      <SkeletonLoader type="cards" :count="6" />
      <AppLoader size="md" text="Loading academic courses & projects" />
    </div>

    <!-- Empty State -->
    <EmptyState
      v-else-if="!projectStore.items.length"
      class="mt-10"
      title="No courses or projects yet"
      description="Create your first academic project to begin tracking syllabus topics, homework assignments, and deadlines."
    >
      <template #actions>
        <button class="btn-primary gap-2" type="button" @click="openCreateModal">
          <AppIcon name="plus" :size="16" /> Create First Course
        </button>
      </template>
    </EmptyState>

    <!-- Projects Grid -->
    <div v-else class="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="project in filteredProjects"
        :key="project.id"
        class="surface-card group flex flex-col justify-between p-5 transition-all duration-200 hover:-translate-y-1"
      >
        <!-- Top Section -->
        <div>
          <div class="flex items-start justify-between gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-academic-purpleLight text-academic-purple dark:bg-purple-950/60 dark:text-purple-300">
              <AppIcon name="projects" :size="22" />
            </div>

            <div class="flex items-center gap-1">
              <button
                type="button"
                class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
                title="Edit Course"
                @click="openEditModal(project)"
              >
                <AppIcon name="edit" :size="16" />
              </button>
              <button
                type="button"
                class="rounded-lg p-1.5 text-rose-400 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/40"
                title="Delete Course"
                @click="promptDelete(project)"
              >
                <AppIcon name="trash" :size="16" />
              </button>
            </div>
          </div>

          <h2 class="font-display mt-4 text-base font-bold text-slate-900 group-hover:text-brand-600 dark:text-white dark:group-hover:text-brand-400">
            {{ project.name }}
          </h2>

          <p class="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-500 dark:text-slate-400">
            {{ project.description || "No specific syllabus or description added." }}
          </p>
        </div>

        <!-- Bottom Section: Task Count & Actions -->
        <div class="mt-6 border-t border-slate-100 pt-4 dark:border-slate-800">
          <div class="flex items-center justify-between">
            <span class="font-mono text-xs font-bold text-slate-600 dark:text-slate-300">
              {{ project.task_count || 0 }} {{ project.task_count === 1 ? 'Task' : 'Tasks' }}
            </span>

            <button
              type="button"
              class="rounded-md bg-brand-50 px-2 py-1 text-xs font-bold text-brand-700 hover:bg-brand-100 dark:bg-brand-950/60 dark:text-brand-300 dark:hover:bg-brand-900/60"
              @click="openAddTaskModal(project)"
            >
              + Add Task
            </button>
          </div>

          <div class="mt-4 flex items-center justify-end gap-2">
            <router-link
              :to="{ name: 'tasks', query: { project_id: project.id } }"
              class="btn-secondary w-full justify-center text-xs"
            >
              Open Task Ledger &rarr;
            </router-link>
          </div>
        </div>
      </article>
    </div>

    <!-- Create / Edit Project Modal -->
    <ProjectModal
      :is-open="isProjectModalOpen"
      :is-edit="isEditMode"
      :project-data="selectedProject"
      :loading="modalLoading"
      :form-errors="formErrors"
      @close="isProjectModalOpen = false"
      @save="handleSaveProject"
    />

    <!-- Add Task Modal directly inside project -->
    <TaskModal
      :is-open="isTaskModalOpen"
      :projects="projectStore.items"
      :task-data="{ project_id: taskModalProject?.id }"
      :loading="taskLoading"
      :form-errors="taskFormErrors"
      @close="isTaskModalOpen = false"
      @save="handleCreateTask"
    />

    <!-- Confirmation Modal for Delete -->
    <ConfirmModal
      :is-open="isDeleteModalOpen"
      title="Delete Course & Tasks?"
      :message="`Are you sure you want to delete '${projectToDelete?.name}'? Every task and assignment inside it will be permanently removed.`"
      confirm-text="Delete Course"
      :loading="deleteLoading"
      :is-danger="true"
      @close="isDeleteModalOpen = false"
      @cancel="isDeleteModalOpen = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
