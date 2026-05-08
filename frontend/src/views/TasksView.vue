<script setup>
import { onMounted, reactive, ref } from "vue";
import apiClient from "../api/client";
import { useProjectStore } from "../stores/projects";
import { useTaskStore } from "../stores/tasks";

const projectStore = useProjectStore();
const taskStore = useTaskStore();
const formError = ref("");
const formSuccess = ref("");

const form = reactive({
  title: "",
  description: "",
  project_id: "",
  priority: "medium",
  status: "todo",
  deadline: "",
  attachment_url: "",
});

const uploadAttachment = async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post("/uploads", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  form.attachment_url = data.attachment_url;
};

onMounted(async () => {
  await Promise.all([projectStore.fetchProjects(), taskStore.fetchTasks()]);
});

const createTask = async () => {
  formError.value = "";
  formSuccess.value = "";
  if (!form.title.trim()) {
    formError.value = "Task title is required.";
    return;
  }
  if (!form.project_id) {
    formError.value = "Please create/select a project before creating tasks.";
    return;
  }
  try {
    await taskStore.createTask({
      ...form,
      project_id: Number(form.project_id),
      deadline: form.deadline || null,
    });
    formSuccess.value = "Task created successfully.";
    form.title = "";
    form.description = "";
    form.priority = "medium";
    form.status = "todo";
    form.deadline = "";
    form.attachment_url = "";
  } catch (error) {
    formError.value = error.response?.data?.message || "Unable to create task right now.";
  }
};
</script>

<template>
  <div class="page-wrap">
    <section class="panel">
      <h3 class="section-title">Create Task</h3>
      <p class="section-subtitle">Capture work quickly and assign priorities.</p>
      <label>Title</label>
      <input v-model="form.title" type="text" placeholder="Task title" />
      <label>Description</label>
      <textarea v-model="form.description" rows="2" placeholder="Task details"></textarea>
      <label>Project</label>
      <select v-model="form.project_id">
        <option value="">Select project</option>
        <option v-for="project in projectStore.items" :key="project.id" :value="project.id">
          {{ project.name }}
        </option>
      </select>
      <small v-if="!projectStore.items.length">No projects yet. Create one first in Projects page.</small>
      <div class="grid grid-2">
        <div>
          <label>Priority</label>
          <select v-model="form.priority">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <div>
          <label>Status</label>
          <select v-model="form.status">
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        </div>
      </div>
      <label>Deadline</label>
      <input v-model="form.deadline" type="datetime-local" />
      <label>Attachment</label>
      <input type="file" @change="uploadAttachment" />
      <small v-if="form.attachment_url">Uploaded: {{ form.attachment_url }}</small>
      <button @click="createTask">Create Task</button>
      <p v-if="formError" style="color: #fca5a5">{{ formError }}</p>
      <p v-if="formSuccess" style="color: #86efac">{{ formSuccess }}</p>
    </section>

    <section class="panel">
      <div class="title-row">
        <div>
          <h3 class="section-title">Task Board</h3>
          <p class="section-subtitle">View, complete, and remove tasks.</p>
        </div>
        <button class="secondary" @click="taskStore.fetchTasks">Refresh</button>
      </div>
      <div v-if="!taskStore.items.length" class="empty-state">No tasks available yet.</div>
      <div v-for="task in taskStore.items" :key="task.id" class="task-row">
        <div>
          <strong style="font-size: 15px">{{ task.title }}</strong>
          <p class="muted" style="margin: 4px 0 8px">{{ task.description || "No description" }}</p>
          <span :class="`chip ${task.status === 'done' ? 'success' : task.priority === 'high' ? 'warn' : ''}`">
            {{ task.status }} | {{ task.priority }}
          </span>
        </div>
        <div class="inline-actions">
          <button class="secondary" @click="taskStore.completeTask(task.id)">Done</button>
          <button class="danger" @click="taskStore.deleteTask(task.id)">Delete</button>
        </div>
      </div>
    </section>
  </div>
</template>
