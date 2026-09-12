import { reactive } from "vue";

export const toastState = reactive({ items: [] });

let nextToastId = 1;

export const showToast = (message, type = "success") => {
  const id = nextToastId++;
  toastState.items.push({ id, message, type });
  window.setTimeout(() => dismissToast(id), 4000);
};

export const dismissToast = (id) => {
  toastState.items = toastState.items.filter((toast) => toast.id !== id);
};
