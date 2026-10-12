import { reactive } from "vue";

export const toastState = reactive({ items: [] });

let nextToastId = 1;

export const showToast = (message, type = "success") => {
  // Dedupe identical toasts fired in quick succession (double-clicks, overlapping
  // refresh paths) so the stack never shows the same message twice.
  const duplicate = toastState.items.some((toast) => toast.message === message && toast.type === type);
  if (duplicate) return;
  const id = nextToastId++;
  toastState.items.push({ id, message, type });
  window.setTimeout(() => dismissToast(id), 4000);
};

export const dismissToast = (id) => {
  toastState.items = toastState.items.filter((toast) => toast.id !== id);
};
