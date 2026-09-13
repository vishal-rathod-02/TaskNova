/**
 * Utility for parsing and updating Markdown Checkpoint Subtasks (- [ ] / - [x])
 */

export const parseSubtasks = (text) => {
  if (!text || typeof text !== "string") {
    return { items: [], total: 0, completed: 0, percentage: 0 };
  }

  const lines = text.split("\n");
  const items = [];

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    const matchUnchecked = trimmed.match(/^[-*]\s+\[\s*\]\s+(.+)$/);
    const matchChecked = trimmed.match(/^[-*]\s+\[[xX]\]\s+(.+)$/);

    if (matchUnchecked) {
      items.push({ lineIndex: index, title: matchUnchecked[1].trim(), completed: false });
    } else if (matchChecked) {
      items.push({ lineIndex: index, title: matchChecked[1].trim(), completed: true });
    }
  });

  const total = items.length;
  const completed = items.filter((i) => i.completed).length;
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  return { items, total, completed, percentage };
};

export const toggleSubtaskInText = (text, subtaskIndex) => {
  if (!text || typeof text !== "string") return text;
  const lines = text.split("\n");
  let foundCount = 0;

  for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trim();
    const isUnchecked = /^[-*]\s+\[\s*\]\s+/.test(trimmed);
    const isChecked = /^[-*]\s+\[[xX]\]\s+/.test(trimmed);

    if (isUnchecked || isChecked) {
      if (foundCount === subtaskIndex) {
        if (isUnchecked) {
          lines[i] = lines[i].replace(/^([-*]\s+\[)\s*(\]\s+)/, "$1x$2");
        } else {
          lines[i] = lines[i].replace(/^([-*]\s+\[)[xX](\]\s+)/, "$1 $2");
        }
        break;
      }
      foundCount++;
    }
  }

  return lines.join("\n");
};

export const addSubtaskToText = (text, newTitle) => {
  const cleanTitle = newTitle.trim();
  if (!cleanTitle) return text;
  const prefix = text && text.trim().length > 0 ? (text.endsWith("\n") ? "" : "\n") : "";
  return `${text || ""}${prefix}- [ ] ${cleanTitle}`;
};
