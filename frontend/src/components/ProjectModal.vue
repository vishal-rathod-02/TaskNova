<script setup>
import { reactive, watch } from "vue";
import AppIcon from "./AppIcon.vue";

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  isEdit: { type: Boolean, default: false },
  projectData: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  formErrors: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["save", "close"]);

const form = reactive({
  name: "",
  description: "",
});

const courseTemplates = [
  "Data Structures & Algorithms",
  "Web Application Development",
  "Database Management Systems",
  "Operating Systems Lab",
  "Senior Capstone Project",
  "Machine Learning & AI",
];

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      document.body.style.overflow = "hidden";
      if (props.isEdit && props.projectData) {
        form.name = props.projectData.name || "";
        form.description = props.projectData.description || "";
      } else {
        form.name = "";
        form.description = "";
      }
    } else {
      document.body.style.overflow = "";
    }
  },
  { immediate: true }
);

const selectTemplate = (name) => {
  form.name = name;
};

const submitForm = () => {
  emit("save", { ...form });
};
</script>

<template>
  <Teleport to="body">
    <!-- Rigid Backdrop: Clicking outside does NOT close -->
    <div v-if="isOpen" class="modal-backdrop z-50 animate-fade-in">
      <div class="modal-panel max-w-lg animate-scale-in" role="dialog" aria-modal="true">
        <div class="flex items-center justify-between border-b border-slate-100 pb-4 dark:border-slate-800">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-academic-purpleLight text-academic-purple dark:bg-purple-950/60 dark:text-purple-300">
              <AppIcon name="projects" :size="20" />
            </div>
            <div>
              <h2 class="font-display text-lg font-bold text-slate-900 dark:text-white">
                {{ isEdit ? "Edit Course / Project" : "New Course / Project" }}
              </h2>
              <p class="text-xs text-slate-500 dark:text-slate-400">
                {{ isEdit ? "Update course details and description." : "Organize your subjects, research labs, or project teams." }}
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
          <!-- Course Name -->
          <div>
            <label class="field-label" for="project-name">Project / Course Name <span class="text-rose-500">*</span></label>
            <input
              id="project-name"
              v-model="form.name"
              class="input-field"
              type="text"
              maxlength="120"
              placeholder="e.g. Distributed Systems (CS420)"
              required
              autofocus
            />
            <span v-if="formErrors.name" class="field-error"><AppIcon name="info" :size="14" />{{ formErrors.name }}</span>
          </div>

          <!-- Quick Suggestions -->
          <div v-if="!isEdit">
            <label class="field-label">Quick Suggestions</label>
            <div class="mt-1.5 flex flex-wrap gap-1.5">
              <button
                v-for="tpl in courseTemplates"
                :key="tpl"
                type="button"
                class="rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700 transition-colors hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700 dark:border-slate-800 dark:bg-night-card dark:text-slate-300 dark:hover:border-brand-700 dark:hover:bg-brand-950/40 dark:hover:text-brand-300"
                @click="selectTemplate(tpl)"
              >
                {{ tpl }}
              </button>
            </div>
          </div>

          <!-- Description -->
          <div>
            <label class="field-label" for="project-desc">Course Description & Goals</label>
            <textarea
              id="project-desc"
              v-model="form.description"
              class="input-field min-h-24 resize-y"
              maxlength="5000"
              placeholder="Syllabus objectives, faculty details, semester milestones, or team members..."
            ></textarea>
            <span class="field-help">Helps you structure all related tasks and deliverables.</span>
            <span v-if="formErrors.description" class="field-error"><AppIcon name="info" :size="14" />{{ formErrors.description }}</span>
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
              {{ loading ? "Saving..." : (isEdit ? "Save Changes" : "Create Project") }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
