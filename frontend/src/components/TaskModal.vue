<script setup>
import { computed, reactive, ref, watch } from "vue";
import AcademicNotes from "./AcademicNotes.vue";
import AppIcon from "./AppIcon.vue";

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  isEdit: { type: Boolean, default: false },
  taskData: { type: Object, default: () => ({}) },
  projects: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  formErrors: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["save", "close"]);

const isPreviewMode = ref(false);

const form = reactive({
  title: "",
  description: "",
  project_id: "",
  priority: "medium",
  status: "todo",
  due_date: "",
});

const toLocalInput = (iso) => {
  if (!iso) return "";
  const date = new Date(iso);
  const pad = (value) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
};

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      document.body.style.overflow = "hidden";
      isPreviewMode.value = false;
      if (props.isEdit && props.taskData) {
        form.title = props.taskData.title || "";
        form.description = props.taskData.description || "";
        form.project_id = props.taskData.project_id || "";
        form.priority = props.taskData.priority || "medium";
        form.status = props.taskData.status || "todo";
        form.due_date = toLocalInput(props.taskData.due_date);
      } else {
        form.title = props.taskData?.title || "";
        form.description = props.taskData?.description || "";
        form.project_id = props.taskData?.project_id || (props.projects[0]?.id || "");
        form.priority = "medium";
        form.status = props.taskData?.status || "todo";
        form.due_date = props.taskData?.due_date ? toLocalInput(props.taskData.due_date) : "";
      }
    } else {
      document.body.style.overflow = "";
    }
  },
  { immediate: true }
);

const insertTextIntoDescription = (template) => {
  const prefix = form.description && !form.description.endsWith("\n") ? "\n" : "";
  form.description = `${form.description || ""}${prefix}${template}`;
};

const setPresetDate = (daysFromNow) => {
  if (daysFromNow === null) {
    form.due_date = "";
    return;
  }
  const d = new Date();
  d.setDate(d.getDate() + daysFromNow);
  d.setHours(18, 0, 0, 0); // Default to 6:00 PM
  const pad = (v) => String(v).padStart(2, "0");
  form.due_date = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

const submitForm = () => {
  emit("save", { ...form });
};
</script>

<template>
  <Teleport to="body">
    <!-- Rigid Backdrop: Clicking outside does NOT close -->
    <div v-if="isOpen" class="modal-backdrop z-50 animate-fade-in">
      <div class="modal-panel max-w-xl animate-scale-in" role="dialog" aria-modal="true">
        <div class="flex items-center justify-between border-b border-slate-100 pb-4 dark:border-slate-800">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-950/60 dark:text-brand-300">
              <AppIcon :name="isEdit ? 'edit' : 'plus'" :size="20" />
            </div>
            <div>
              <h2 class="font-display text-lg font-bold text-slate-900 dark:text-white">
                {{ isEdit ? "Edit Task" : "Create New Task" }}
              </h2>
              <p class="text-xs text-slate-500 dark:text-slate-400">
                {{ isEdit ? "Update details in your academic task ledger." : "Add assignments, course work, or study items." }}
              </p>
            </div>
          </div>
          <button
            type="button"
            class="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
            @click="emit('close')"
          >
            <AppIcon name="x" :size="18" />
          </button>
        </div>

        <form class="mt-5 space-y-4" @submit.prevent="submitForm">
          <!-- Title -->
          <div>
            <label class="field-label" for="task-title">Task Title <span class="text-rose-500">*</span></label>
            <input
              id="task-title"
              v-model="form.title"
              class="input-field"
              type="text"
              maxlength="160"
              placeholder="e.g. Complete CS101 Algorithm Analysis Assignment"
              required
              autofocus
            />
            <span v-if="formErrors.title" class="field-error"><AppIcon name="info" :size="14" />{{ formErrors.title }}</span>
          </div>

          <!-- Description & Markdown Notes with Helpers -->
          <div>
            <div class="flex items-center justify-between">
              <label class="field-label" for="task-desc">Description, Checkpoints & Formula Notes</label>
              
              <!-- Editor / Preview Toggle -->
              <div class="flex items-center gap-1 rounded-lg bg-slate-100 p-0.5 dark:bg-night-card">
                <button
                  type="button"
                  class="rounded px-2 py-0.5 text-[11px] font-semibold transition-all"
                  :class="!isPreviewMode ? 'bg-white text-slate-900 shadow-sm dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-900 dark:text-slate-400'"
                  @click="isPreviewMode = false"
                >
                  Edit
                </button>
                <button
                  type="button"
                  class="rounded px-2 py-0.5 text-[11px] font-semibold transition-all"
                  :class="isPreviewMode ? 'bg-white text-slate-900 shadow-sm dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-900 dark:text-slate-400'"
                  @click="isPreviewMode = true"
                >
                  Preview
                </button>
              </div>
            </div>

            <!-- Quick Template Insert Shortcuts -->
            <div v-if="!isPreviewMode" class="mt-1.5 flex flex-wrap items-center gap-1.5 text-[11px]">
              <span class="text-slate-400 font-mono text-[10px]">Insert:</span>
              <button
                type="button"
                class="rounded bg-slate-100 px-1.5 py-0.5 text-slate-600 hover:bg-brand-50 hover:text-brand-700 dark:bg-slate-800 dark:text-slate-300"
                @click="insertTextIntoDescription('- [ ] Subtask checkpoint')"
              >
                + Checkpoint
              </button>
              <button
                type="button"
                class="rounded bg-slate-100 px-1.5 py-0.5 text-slate-600 hover:bg-brand-50 hover:text-brand-700 dark:bg-slate-800 dark:text-slate-300"
                @click="insertTextIntoDescription('```\n// Code snippet\n```')"
              >
                + Code Block
              </button>
              <button
                type="button"
                class="rounded bg-slate-100 px-1.5 py-0.5 text-slate-600 hover:bg-brand-50 hover:text-brand-700 dark:bg-slate-800 dark:text-slate-300"
                @click="insertTextIntoDescription('$$E = mc^2$$')"
              >
                + Math Formula
              </button>
            </div>

            <!-- Text Area / Live Preview -->
            <div v-if="isPreviewMode" class="mt-1.5 min-h-24 max-h-48 overflow-y-auto rounded-xl border border-slate-200 bg-slate-50/50 p-3.5 dark:border-slate-700 dark:bg-night-surface">
              <AcademicNotes v-if="form.description" :content="form.description" />
              <p v-else class="text-xs italic text-slate-400">Nothing to preview yet.</p>
            </div>
            <textarea
              v-else
              id="task-desc"
              v-model="form.description"
              class="input-field min-h-24 resize-y font-sans text-xs"
              maxlength="10000"
              placeholder="Include syllabus instructions, checkpoints (- [ ] task), formulas ($$...$$), or study notes..."
            ></textarea>
            <span v-if="formErrors.description" class="field-error"><AppIcon name="info" :size="14" />{{ formErrors.description }}</span>
          </div>

          <!-- Project & Priority Grid -->
          <div class="grid gap-4 sm:grid-cols-2">
            <!-- Project / Course Selector -->
            <div>
              <label class="field-label" for="task-project">Course / Project <span class="text-rose-500">*</span></label>
              <select
                id="task-project"
                v-model="form.project_id"
                class="input-field"
                required
              >
                <option value="" disabled>Select Course / Project</option>
                <option v-for="p in projects" :key="p.id" :value="p.id">
                  {{ p.name }}
                </option>
              </select>
              <span v-if="formErrors.project_id" class="field-error"><AppIcon name="info" :size="14" />{{ formErrors.project_id }}</span>
            </div>

            <!-- Priority Selector -->
            <div>
              <label class="field-label">Priority Level</label>
              <div class="mt-1.5 grid grid-cols-3 gap-1.5">
                <button
                  type="button"
                  :class="form.priority === 'low' ? 'bg-slate-200 text-slate-800 font-bold dark:bg-slate-700 dark:text-white border-slate-400' : 'bg-slate-50 text-slate-600 dark:bg-night-card dark:text-slate-400 border-slate-200 dark:border-slate-800'"
                  class="rounded-xl border py-2 text-xs font-semibold transition-all hover:bg-slate-100 dark:hover:bg-slate-800"
                  @click="form.priority = 'low'"
                >
                  Low
                </button>
                <button
                  type="button"
                  :class="form.priority === 'medium' ? 'bg-amber-100 text-amber-900 border-amber-400 font-bold dark:bg-amber-950/60 dark:text-amber-200' : 'bg-slate-50 text-slate-600 dark:bg-night-card dark:text-slate-400 border-slate-200 dark:border-slate-800'"
                  class="rounded-xl border py-2 text-xs font-semibold transition-all hover:bg-amber-50 dark:hover:bg-amber-950/40"
                  @click="form.priority = 'medium'"
                >
                  Medium
                </button>
                <button
                  type="button"
                  :class="form.priority === 'high' ? 'bg-rose-100 text-rose-900 border-rose-400 font-bold dark:bg-rose-950/60 dark:text-rose-200' : 'bg-slate-50 text-slate-600 dark:bg-night-card dark:text-slate-400 border-slate-200 dark:border-slate-800'"
                  class="rounded-xl border py-2 text-xs font-semibold transition-all hover:bg-rose-50 dark:hover:bg-rose-950/40"
                  @click="form.priority = 'high'"
                >
                  High
                </button>
              </div>
            </div>
          </div>

          <!-- Status & Due Date Grid -->
          <div class="grid gap-4 sm:grid-cols-2">
            <!-- Status -->
            <div>
              <label class="field-label">Status</label>
              <div class="mt-1.5 grid grid-cols-3 gap-1.5">
                <button
                  type="button"
                  :class="form.status === 'todo' ? 'bg-brand-50 text-brand-700 border-brand-400 font-bold dark:bg-brand-950/60 dark:text-brand-300' : 'bg-slate-50 text-slate-600 dark:bg-night-card dark:text-slate-400 border-slate-200 dark:border-slate-800'"
                  class="rounded-xl border py-2 text-xs font-semibold transition-all"
                  @click="form.status = 'todo'"
                >
                  To Do
                </button>
                <button
                  type="button"
                  :class="form.status === 'in_progress' ? 'bg-amber-50 text-amber-700 border-amber-400 font-bold dark:bg-amber-950/60 dark:text-amber-300' : 'bg-slate-50 text-slate-600 dark:bg-night-card dark:text-slate-400 border-slate-200 dark:border-slate-800'"
                  class="rounded-xl border py-2 text-xs font-semibold transition-all"
                  @click="form.status = 'in_progress'"
                >
                  In Progress
                </button>
                <button
                  type="button"
                  :class="form.status === 'done' ? 'bg-emerald-50 text-emerald-700 border-emerald-400 font-bold dark:bg-emerald-950/60 dark:text-emerald-300' : 'bg-slate-50 text-slate-600 dark:bg-night-card dark:text-slate-400 border-slate-200 dark:border-slate-800'"
                  class="rounded-xl border py-2 text-xs font-semibold transition-all"
                  @click="form.status = 'done'"
                >
                  Done
                </button>
              </div>
            </div>

            <!-- Due Date & Presets -->
            <div>
              <label class="field-label" for="task-due">Due Date & Time</label>
              <input
                id="task-due"
                v-model="form.due_date"
                class="input-field"
                type="datetime-local"
              />
              <div class="mt-2 flex flex-wrap gap-1">
                <button
                  type="button"
                  class="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 hover:bg-brand-50 hover:text-brand-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-white"
                  @click="setPresetDate(0)"
                >
                  Today
                </button>
                <button
                  type="button"
                  class="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 hover:bg-brand-50 hover:text-brand-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-white"
                  @click="setPresetDate(1)"
                >
                  Tomorrow
                </button>
                <button
                  type="button"
                  class="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 hover:bg-brand-50 hover:text-brand-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-white"
                  @click="setPresetDate(7)"
                >
                  Next Week
                </button>
                <button
                  v-if="form.due_date"
                  type="button"
                  class="rounded-md bg-rose-50 px-2 py-0.5 text-[11px] font-medium text-rose-600 hover:bg-rose-100 dark:bg-rose-950/40 dark:text-rose-400"
                  @click="setPresetDate(null)"
                >
                  Clear
                </button>
              </div>
              <span v-if="formErrors.due_date" class="field-error"><AppIcon name="info" :size="14" />{{ formErrors.due_date }}</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="mt-6 flex flex-wrap items-center justify-end gap-3 border-t border-slate-100 pt-4 dark:border-slate-800">
            <button
              type="button"
              class="btn-secondary"
              @click="emit('close')"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn-primary"
              :disabled="loading"
            >
              <span v-if="loading" class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
              {{ loading ? "Saving..." : (isEdit ? "Save Changes" : "Create Task") }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
