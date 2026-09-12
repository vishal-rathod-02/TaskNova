<script setup>
import { onMounted, reactive, ref } from "vue";
import AppIcon from "../components/AppIcon.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import { showToast } from "../composables/toast";
import { useProjectStore } from "../stores/projects";

const projectStore = useProjectStore();
const creating = ref(false);
const editingId = ref(null);
const error = ref("");
const formErrors = ref({});
const form = reactive({ name: "", description: "" });
const editForm = reactive({ name: "", description: "" });

const requestMessage = (requestError, fallback) => {
  formErrors.value = requestError.response?.data?.errors || {};
  return requestError.response?.data?.message || fallback;
};

const loadProjects = async () => {
  error.value = "";
  try {
    await projectStore.fetchProjects();
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to load projects.");
  }
};

onMounted(loadProjects);

const createProject = async () => {
  error.value = "";
  formErrors.value = {};
  try {
    await projectStore.createProject({ ...form });
    form.name = "";
    form.description = "";
    creating.value = false;
    showToast("Project created.");
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to create project.");
  }
};

const startEdit = (project) => {
  editingId.value = project.id;
  editForm.name = project.name;
  editForm.description = project.description || "";
  error.value = "";
  formErrors.value = {};
};

const saveProject = async (projectId) => {
  error.value = "";
  formErrors.value = {};
  try {
    await projectStore.updateProject(projectId, { ...editForm });
    editingId.value = null;
    showToast("Project updated.");
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to update project.");
  }
};

const removeProject = async (project) => {
  if (!window.confirm(`Delete "${project.name}" and every task inside it?`)) return;
  error.value = "";
  try {
    await projectStore.deleteProject(project.id);
    showToast("Project deleted.");
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to delete project.");
  }
};
</script>

<template>
  <div class="page-shell">
    <PageHeader title="Projects" description="A clean ledger for each piece of work you own.">
      <template #actions>
        <button class="btn-primary gap-2" type="button" @click="creating = !creating"><AppIcon name="plus" :size="16" />{{ creating ? "Close form" : "Create project" }}</button>
      </template>
    </PageHeader>

    <section v-if="creating" class="surface mt-8 p-6">
      <h2 class="section-title">New project</h2>
      <form class="mt-6 grid gap-5" @submit.prevent="createProject">
        <label class="field-label" for="project-name">Project name
          <input id="project-name" v-model="form.name" class="input-field" type="text" maxlength="120" placeholder="e.g. Product launch" required />
          <span v-if="formErrors.name" class="field-error">{{ formErrors.name }}</span>
        </label>
        <label class="field-label" for="project-description">Description
          <textarea id="project-description" v-model="form.description" class="input-field min-h-28 resize-y" maxlength="5000" placeholder="What is this project for?"></textarea>
          <span class="field-help">Optional context for your future self.</span>
          <span v-if="formErrors.description" class="field-error">{{ formErrors.description }}</span>
        </label>
        <div class="flex flex-wrap gap-3"><button class="btn-primary" type="submit">Create project</button><button class="btn-secondary" type="button" @click="creating = false">Cancel</button></div>
      </form>
    </section>

    <p v-if="error" class="field-error mt-6" aria-live="polite">{{ error }}</p>
    <section class="mt-10">
      <div class="flex items-end justify-between gap-4"><div><h2 class="section-title">Your projects</h2><p class="mt-2 body-copy">Open a project to add and track its work.</p></div><button class="btn-secondary gap-2" type="button" :disabled="projectStore.loading" @click="loadProjects"><AppIcon name="refresh" :size="16" />{{ projectStore.loading ? "Refreshing..." : "Refresh" }}</button></div>
      <p v-if="projectStore.loading" class="mt-8 text-sm text-slate dark:text-[#9AA3B2]">Loading projects...</p>
      <EmptyState v-else-if="!projectStore.items.length" class="mt-8" title="No projects yet" description="Create your first project to start tracking meaningful work." />
      <div v-else class="mt-6 border-t border-slate/20 dark:border-slate/30">
        <article v-for="project in projectStore.items" :key="project.id" class="ledger-row">
          <template v-if="editingId === project.id">
            <span class="priority-tab priority-medium" aria-hidden="true"></span>
            <form class="col-span-full grid gap-4" @submit.prevent="saveProject(project.id)">
              <label class="field-label">Project name<input v-model="editForm.name" class="input-field" type="text" maxlength="120" required /></label>
              <label class="field-label">Description<textarea v-model="editForm.description" class="input-field min-h-24 resize-y" maxlength="5000"></textarea></label>
              <div class="flex flex-wrap gap-3"><button class="btn-primary" type="submit">Save changes</button><button class="btn-secondary" type="button" @click="editingId = null">Cancel</button></div>
            </form>
          </template>
          <template v-else>
            <span class="priority-tab priority-medium" aria-hidden="true"></span>
            <div class="min-w-0"><h3 class="text-base font-medium text-ink dark:text-[#E7E9ED]">{{ project.name }}</h3><p class="mt-1 max-w-[72ch] text-sm leading-5 text-slate dark:text-[#9AA3B2]">{{ project.description || "No description yet." }}</p><p class="mt-2 data-label">{{ project.task_count || 0 }} tasks</p></div>
            <div class="flex flex-wrap gap-x-3 gap-y-1 sm:justify-end"><router-link class="min-h-11 px-1 py-3 text-sm font-medium text-ink underline decoration-slate/50 underline-offset-4 hover:decoration-ink dark:text-[#E7E9ED]" :to="{ name: 'tasks', query: { project_id: project.id } }">View tasks</router-link><button class="min-h-11 px-1 text-sm font-medium text-ink underline decoration-slate/50 underline-offset-4 hover:decoration-ink dark:text-[#E7E9ED]" type="button" @click="startEdit(project)">Edit</button><button class="btn-danger" type="button" @click="removeProject(project)">Delete project</button></div>
          </template>
        </article>
      </div>
    </section>
  </div>
</template>
