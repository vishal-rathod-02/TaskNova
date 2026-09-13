<script setup>
import { computed } from "vue";
import { parseSubtasks } from "../utils/subtasks";

const props = defineProps({
  content: { type: String, default: "" },
  editable: { type: Boolean, default: false },
});

const emit = defineEmits(["toggle-subtask"]);

const subtaskData = computed(() => parseSubtasks(props.content));

// HTML sanitizer and simple Markdown parser
const parsedHtml = computed(() => {
  if (!props.content) return "";

  const lines = props.content.split("\n");
  let html = "";
  let inCodeBlock = false;
  let codeBuffer = [];
  let inList = false;

  const escapeHtml = (str) =>
    str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");

  const formatInline = (text) => {
    let t = escapeHtml(text);

    // Math equation blocks: $$...$$ or $...$
    t = t.replace(/\$\$(.+?)\$\$/g, '<span class="font-mono px-1.5 py-0.5 rounded bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300 font-semibold border border-brand-200 dark:border-brand-800">$1</span>');
    t = t.replace(/\$([^\$]+?)\$/g, '<span class="font-mono text-xs px-1 rounded bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200">$1</span>');

    // Bold
    t = t.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    // Italic
    t = t.replace(/\*(.+?)\*/g, "<em>$1</em>");
    // Inline code
    t = t.replace(/`([^`]+)`/g, '<code class="font-mono text-xs px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 dark:bg-night-surface dark:text-brand-300 border border-slate-200 dark:border-slate-800">$1</code>');
    // Links
    t = t.replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-brand-600 underline dark:text-brand-400 font-medium">$1</a>');

    return t;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Code block check
    if (line.trim().startsWith("```")) {
      if (inCodeBlock) {
        html += `<pre class="my-2 p-3 rounded-xl bg-slate-900 text-slate-100 font-mono text-xs overflow-x-auto border border-slate-800"><code>${codeBuffer.join("\n")}</code></pre>`;
        codeBuffer = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeBuffer.push(escapeHtml(line));
      continue;
    }

    // Checkboxes are handled separately in structured UI, but if present in general notes, format them nicely
    if (/^[-*]\s+\[[\sxX]\]\s+/.test(line.trim())) {
      continue; // Skip rendering here, they are shown in the subtask checklist section
    }

    // Headers
    if (line.startsWith("### ")) {
      html += `<h4 class="font-display font-bold text-sm text-slate-900 dark:text-white mt-3 mb-1">${formatInline(line.substring(4))}</h4>`;
      continue;
    }
    if (line.startsWith("## ")) {
      html += `<h3 class="font-display font-bold text-base text-slate-900 dark:text-white mt-4 mb-1.5">${formatInline(line.substring(3))}</h3>`;
      continue;
    }
    if (line.startsWith("# ")) {
      html += `<h2 class="font-display font-extrabold text-lg text-slate-900 dark:text-white mt-4 mb-2">${formatInline(line.substring(2))}</h2>`;
      continue;
    }

    // Blockquote
    if (line.startsWith("> ")) {
      html += `<blockquote class="border-l-4 border-brand-500 pl-3 py-1 my-2 text-xs italic text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-night-surface/50 rounded-r-lg">${formatInline(line.substring(2))}</blockquote>`;
      continue;
    }

    // Bullet points
    if (/^[-*]\s+/.test(line.trim())) {
      const content = line.trim().replace(/^[-*]\s+/, "");
      html += `<li class="ml-4 list-disc text-xs text-slate-700 dark:text-slate-300 my-0.5">${formatInline(content)}</li>`;
      continue;
    }

    // Empty line
    if (!line.trim()) {
      html += '<div class="h-2"></div>';
      continue;
    }

    // Paragraph
    html += `<p class="text-xs leading-relaxed text-slate-700 dark:text-slate-300 my-1">${formatInline(line)}</p>`;
  }

  return html;
});
</script>

<template>
  <div class="space-y-4">
    <!-- Interactive Subtasks / Checkpoint Checklist Section -->
    <div
      v-if="subtaskData.total > 0"
      class="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5 dark:border-slate-800 dark:bg-night-surface"
    >
      <div class="flex items-center justify-between mb-3">
        <span class="data-label !text-[11px]">Syllabus Checkpoints & Subtasks</span>
        <span class="font-mono text-xs font-bold text-slate-700 dark:text-slate-300">
          {{ subtaskData.completed }}/{{ subtaskData.total }} Completed ({{ subtaskData.percentage }}%)
        </span>
      </div>

      <!-- Mini Progress bar -->
      <div class="mb-3.5 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
        <div
          class="h-full rounded-full transition-all duration-300"
          :class="subtaskData.percentage === 100 ? 'bg-emerald-500' : 'bg-brand-500'"
          :style="{ width: `${subtaskData.percentage}%` }"
        ></div>
      </div>

      <!-- Checklist Items -->
      <div class="space-y-2">
        <div
          v-for="(item, idx) in subtaskData.items"
          :key="idx"
          class="flex items-start gap-2.5 rounded-lg p-1.5 transition-colors hover:bg-white/80 dark:hover:bg-night-card"
        >
          <input
            type="checkbox"
            :checked="item.completed"
            class="mt-0.5 h-4 w-4 rounded accent-brand-600 transition-transform active:scale-90 cursor-pointer"
            @change="emit('toggle-subtask', idx)"
          />
          <span
            class="text-xs text-slate-800 dark:text-slate-200 transition-all cursor-pointer select-none"
            :class="{ 'line-through text-slate-400 dark:text-slate-500': item.completed }"
            @click="emit('toggle-subtask', idx)"
          >
            {{ item.title }}
          </span>
        </div>
      </div>
    </div>

    <!-- Rendered Markdown Notes -->
    <div
      v-if="parsedHtml"
      class="academic-prose text-xs text-slate-700 dark:text-slate-300 leading-relaxed"
      v-html="parsedHtml"
    ></div>
  </div>
</template>
