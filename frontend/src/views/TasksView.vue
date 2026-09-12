<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import AppIcon from "../components/AppIcon.vue";
import EmptyState from "../components/EmptyState.vue";
import PageHeader from "../components/PageHeader.vue";
import TaskLedgerRow from "../components/TaskLedgerRow.vue";
import { showToast } from "../composables/toast";
import { getTaskActivity } from "../services/tasks";
import { useProjectStore } from "../stores/projects";
import { useTaskStore } from "../stores/tasks";

const route = useRoute();
const projectStore = useProjectStore();
const taskStore = useTaskStore();
const creating = ref(false);
const editingId = ref(null);
const activityTaskId = ref(null);
const activity = ref([]);
const activityLoading = ref(false);
const error = ref("");
const activityError = ref("");
const formErrors = ref({});
const filters = reactive({
  project_id: route.query.project_id || "",
  status: "",
  priority: "",
  due_from: "",
  due_to: "",
});
const form = reactive({ title: "", description: "", project_id: route.query.project_id || "", priority: "medium", status: "todo", due_date: "" });
const editForm = reactive({ title: "", description: "", priority: "medium", status: "todo", due_date: "" });

const projectName = computed(() => projectStore.items.find((project) => project.id === Number(filters.project_id))?.name || "All projects");
const hasProjects = computed(() => projectStore.items.length > 0);

const requestMessage = (requestError, fallback) => {
  formErrors.value = requestError.response?.data?.errors || {};
  return requestError.response?.data?.message || fallback;
};

const loadTasks = async () => {
  error.value = "";
  try {
    await taskStore.fetchTasks(filters);
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to load tasks.");
  }
};

onMounted(async () => {
  try {
    await projectStore.fetchProjects();
    await loadTasks();
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to load your task ledger.");
  }
});

const clearFilters = () => {
  Object.assign(filters, { project_id: "", status: "", priority: "", due_from: "", due_to: "" });
  loadTasks();
};

const resetForm = () => Object.assign(form, { title: "", description: "", project_id: filters.project_id || "", priority: "medium", status: "todo", due_date: "" });

// datetime-local carries no zone, so normalize to a UTC instant before POST:
// otherwise the server would compare a local wall-clock against its UTC clock.
const toUtcIso = (localInput) => (localInput ? new Date(localInput).toISOString() : null);

// API instants (with zone) back to the wall-clock the datetime-local input needs.
const toLocalInput = (iso) => {
  if (!iso) return "";
  const date = new Date(iso);
  const pad = (value) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
};

const createTask = async () => {
  error.value = "";
  formErrors.value = {};
  try {
    await taskStore.createTask({ ...form, project_id: Number(form.project_id), due_date: toUtcIso(form.due_date) });
    resetForm();
    creating.value = false;
    await loadTasks();
    showToast("Task added to the ledger.");
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to create task.");
  }
};

const startEdit = (task) => {
  editingId.value = task.id;
  Object.assign(editForm, { title: task.title, description: task.description || "", priority: task.priority, status: task.status, due_date: toLocalInput(task.due_date) });
  formErrors.value = {};
  error.value = "";
};

const saveTask = async (taskId) => {
  error.value = "";
  formErrors.value = {};
  try {
    await taskStore.updateTask(taskId, { ...editForm, due_date: toUtcIso(editForm.due_date) });
    editingId.value = null;
    showToast("Task updated.");
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to update task.");
  }
};

const toggleStatus = async (task) => {
  error.value = "";
  try {
    if (task.status === "done") await taskStore.updateTask(task.id, { status: "todo" });
    else await taskStore.completeTask(task.id);
    showToast(task.status === "done" ? "Task reopened." : "Task marked done.");
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to update task status.");
  }
};

const removeTask = async (task) => {
  if (!window.confirm(`Delete "${task.title}"?`)) return;
  error.value = "";
  try {
    await taskStore.deleteTask(task.id);
    if (activityTaskId.value === task.id) activityTaskId.value = null;
    showToast("Task deleted.");
  } catch (requestError) {
    error.value = requestMessage(requestError, "Unable to delete task.");
  }
};

const toggleActivity = async (task) => {
  if (activityTaskId.value === task.id) {
    activityTaskId.value = null;
    return;
  }
  activityTaskId.value = task.id;
  activityLoading.value = true;
  activityError.value = "";
  try {
    const { data } = await getTaskActivity(task.id);
    activity.value = data.activity;
  } catch (requestError) {
    activityError.value = requestError.response?.data?.message || "Unable to load task activity.";
  } finally {
    activityLoading.value = false;
  }
};

const activityLabel = (entry) => ({ created: "Created task", updated: "Updated task", status_changed: "Changed status", deleted: "Deleted task" }[entry.action] || entry.action.replaceAll("_", " "));
const formatActivityDate = (date) => new Date(date).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
</script>

<template>
  <div class="page-shell">
    <PageHeader
      title="Tasks"
      :description="projectName === 'All projects' ? 'Every task in your running account of work.' : `Tasks for ${projectName}.`"
    >
      <template #actions>
        <button class="btn-primary gap-2" type="button" :disabled="!hasProjects" @click="creating = !creating"><AppIcon name="plus" :size="16" />{{ creating ? "Close form" : "Create task" }}</button>
      </template>
    </PageHeader>
    <p v-if="!hasProjects" class="field-help mt-4">Create a <router-link class="font-medium text-ink underline underline-offset-4 dark:text-[#E7E9ED]" to="/projects">project</router-link> before adding tasks.</p>

    <section v-if="creating" class="surface mt-8 p-6">
      <h2 class="section-title">New task</h2>
      <form class="mt-6 grid gap-5 md:grid-cols-2" @submit.prevent="createTask">
        <label class="field-label md:col-span-2">Task title<input v-model="form.title" class="input-field" type="text" maxlength="160" placeholder="What needs to happen?" required /><span v-if="formErrors.title" class="field-error">{{ formErrors.title }}</span></label>
        <label class="field-label md:col-span-2">Description<textarea v-model="form.description" class="input-field min-h-24 resize-y" maxlength="10000" placeholder="Add enough context to make the next action clear."></textarea><span v-if="formErrors.description" class="field-error">{{ formErrors.description }}</span></label>
        <label class="field-label">Project<select v-model="form.project_id" class="input-field" required><option value="">Select project</option><option v-for="project in projectStore.items" :key="project.id" :value="project.id">{{ project.name }}</option></select><span v-if="formErrors.project_id" class="field-error">{{ formErrors.project_id }}</span></label>
        <label class="field-label">Due date<input v-model="form.due_date" class="input-field" type="datetime-local" /><span class="field-help">Optional. Dates appear in your local time.</span><span v-if="formErrors.due_date" class="field-error">{{ formErrors.due_date }}</span></label>
        <label class="field-label">Priority<select v-model="form.priority" class="input-field"><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select><span v-if="formErrors.priority" class="field-error">{{ formErrors.priority }}</span></label>
        <label class="field-label">Status<select v-model="form.status" class="input-field"><option value="todo">To do</option><option value="in_progress">In progress</option><option value="done">Done</option></select><span v-if="formErrors.status" class="field-error">{{ formErrors.status }}</span></label>
        <div class="flex flex-wrap gap-3 md:col-span-2"><button class="btn-primary" type="submit">Create task</button><button class="btn-secondary" type="button" @click="creating = false">Cancel</button></div>
      </form>
    </section>

    <p v-if="error" class="field-error mt-6" aria-live="polite">{{ error }}</p>
    <section class="mt-10">
      <div class="flex flex-wrap items-end justify-between gap-4"><div><h2 class="section-title">Task ledger</h2><p class="mt-2 body-copy">Filter the account to focus on the work that needs attention.</p></div><button class="btn-secondary gap-2" type="button" :disabled="taskStore.loading" @click="loadTasks"><AppIcon name="refresh" :size="16" />{{ taskStore.loading ? "Refreshing..." : "Refresh" }}</button></div>
      <form class="mt-6 grid gap-3 border-y border-slate/20 py-5 sm:grid-cols-2 lg:grid-cols-5 dark:border-slate/30" @submit.prevent="loadTasks">
        <label class="field-label">Project<select v-model="filters.project_id" class="input-field"><option value="">All projects</option><option v-for="project in projectStore.items" :key="project.id" :value="project.id">{{ project.name }}</option></select></label>
        <label class="field-label">Status<select v-model="filters.status" class="input-field"><option value="">All statuses</option><option value="todo">To do</option><option value="in_progress">In progress</option><option value="done">Done</option></select></label>
        <label class="field-label">Priority<select v-model="filters.priority" class="input-field"><option value="">All priorities</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select></label>
        <label class="field-label">Due from<input v-model="filters.due_from" class="input-field" type="date" /></label>
        <label class="field-label">Due to<input v-model="filters.due_to" class="input-field" type="date" /></label>
        <div class="flex flex-wrap gap-3 sm:col-span-2 lg:col-span-5"><button class="btn-primary" type="submit">Apply filters</button><button class="btn-secondary" type="button" @click="clearFilters">Clear filters</button></div>
      </form>

      <p v-if="taskStore.loading" class="mt-8 text-sm text-slate dark:text-[#9AA3B2]">Loading tasks...</p>
      <EmptyState v-else-if="!taskStore.items.length" class="mt-8" title="No tasks match this view" description="Try clearing a filter, or add the next task you want to track." />
      <div v-else class="mt-6 border-t border-slate/20 dark:border-slate/30">
        <p class="data-label border-b border-slate/20 py-3 dark:border-slate/30">Showing {{ taskStore.items.length }} of {{ taskStore.pagination.total }} tasks</p>
        <template v-for="task in taskStore.items" :key="task.id">
          <article v-if="editingId === task.id" class="ledger-row">
            <span class="priority-tab" :class="`priority-${editForm.priority}`" aria-hidden="true"></span>
            <form class="col-span-full grid gap-4 md:grid-cols-2" @submit.prevent="saveTask(task.id)">
              <label class="field-label md:col-span-2">Task title<input v-model="editForm.title" class="input-field" type="text" maxlength="160" required /><span v-if="formErrors.title" class="field-error">{{ formErrors.title }}</span></label>
              <label class="field-label md:col-span-2">Description<textarea v-model="editForm.description" class="input-field min-h-24 resize-y" maxlength="10000"></textarea></label>
              <label class="field-label">Priority<select v-model="editForm.priority" class="input-field"><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></label>
              <label class="field-label">Status<select v-model="editForm.status" class="input-field"><option value="todo">To do</option><option value="in_progress">In progress</option><option value="done">Done</option></select></label>
              <label class="field-label">Due date<input v-model="editForm.due_date" class="input-field" type="datetime-local" /><span v-if="formErrors.due_date" class="field-error">{{ formErrors.due_date }}</span></label>
              <div class="flex flex-wrap items-end gap-3"><button class="btn-primary" type="submit">Save changes</button><button class="btn-secondary" type="button" @click="editingId = null">Cancel</button></div>
            </form>
          </article>
          <TaskLedgerRow v-else :task="task" @toggle-status="toggleStatus" @edit="startEdit" @show-activity="toggleActivity" @delete="removeTask" />
          <section v-if="activityTaskId === task.id" class="border-b border-slate/20 bg-paper/60 px-6 py-5 dark:border-slate/30 dark:bg-white/5">
            <p v-if="activityLoading" class="text-sm text-slate dark:text-[#9AA3B2]">Loading activity...</p>
            <p v-else-if="activityError" class="field-error">{{ activityError }}</p>
            <p v-else-if="!activity.length" class="text-sm text-slate dark:text-[#9AA3B2]">No activity recorded yet.</p>
            <div v-else class="border-t border-slate/20 dark:border-slate/30"><div v-for="entry in activity" :key="entry.id" class="flex flex-wrap justify-between gap-x-6 gap-y-1 border-b border-slate/20 py-3 text-sm dark:border-slate/30"><span class="text-ink dark:text-[#E7E9ED]"><strong class="font-medium">{{ entry.actor_name }}</strong> {{ activityLabel(entry).toLowerCase() }}</span><span class="data-label">{{ formatActivityDate(entry.created_at) }}</span></div></div>
          </section>
        </template>
      </div>
    </section>
  </div>
</template>
