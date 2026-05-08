<script setup>
import { onMounted, reactive } from "vue";
import { useProjectStore } from "../stores/projects";

const projectStore = useProjectStore();
const form = reactive({
  name: "",
  description: "",
});

onMounted(async () => {
  await projectStore.fetchProjects();
});

const createProject = async () => {
  if (!form.name.trim()) return;
  await projectStore.createProject(form);
  form.name = "";
  form.description = "";
};
</script>

<template>
  <div class="page-wrap">
    <section class="panel">
      <h3 class="section-title">Create Project</h3>
      <p class="section-subtitle">Organize work by client, team, or goal.</p>
      <label>Name</label>
      <input v-model="form.name" type="text" placeholder="Project name" />
      <label>Description</label>
      <textarea v-model="form.description" rows="3" placeholder="Description"></textarea>
      <button @click="createProject">Create</button>
    </section>

    <section class="panel">
      <div class="title-row">
        <div>
          <h3 class="section-title">Your Projects</h3>
          <p class="section-subtitle">Manage and track all active projects.</p>
        </div>
        <button class="secondary" @click="projectStore.fetchProjects">Refresh</button>
      </div>
      <div v-if="projectStore.loading" class="empty-state">Loading projects...</div>
      <div v-else-if="!projectStore.items.length" class="empty-state">No projects yet. Create your first project above.</div>
      <div v-else class="grid grid-2">
        <article v-for="project in projectStore.items" :key="project.id" class="panel">
          <h4 style="margin: 0 0 8px">{{ project.name }}</h4>
          <p class="muted" style="margin: 0 0 14px">{{ project.description || "No description" }}</p>
          <button class="danger" @click="projectStore.deleteProject(project.id)">Delete</button>
        </article>
      </div>
    </section>
  </div>
</template>
