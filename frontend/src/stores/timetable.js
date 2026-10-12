import { defineStore } from "pinia";
import {
  applyTemplate as applyTemplateRequest,
  autoSchedule as autoScheduleRequest,
  createSlot as createSlotRequest,
  deleteSlot as deleteSlotRequest,
  listAvailableTemplates as listAvailableTemplatesRequest,
  listSlots,
  updateSlot as updateSlotRequest,
} from "../services/timetable";

export const SLOT_TYPES = ["meeting", "focus_work", "operations", "habit", "personal"];

export const SLOT_TYPE_LABELS = {
  meeting: "Meeting",
  focus_work: "Focus Work",
  operations: "Operations",
  habit: "Habit",
  personal: "Personal",
};

export const TEMPLATES = [
  { value: "corporate", label: "Corporate Standard" },
  { value: "maker", label: "Deep Work / Maker" },
  { value: "academic", label: "Campus Routine" },
  { value: "freelance", label: "Freelance Sprint" },
];

export const useTimetableStore = defineStore("timetable", {
  state: () => ({
    items: [],
    loading: false,
    availableTemplates: [],
  }),
  getters: {
    slotsForDay: (state) => (dayOfWeek) =>
      state.items
        .filter((slot) => slot.day_of_week === dayOfWeek && !slot.specific_date)
        .sort((a, b) => a.start_time.localeCompare(b.start_time)),
    slotsForDate: (state) => (isoDate) => {
      if (!isoDate) return [];
      // Backend convention: 0=Mon..6=Sun. JS getDay(): 0=Sun..6=Sat.
      const weekday = (new Date(`${isoDate}T12:00:00`).getDay() + 6) % 7;
      return state.items
        .filter(
          (slot) =>
            slot.specific_date === isoDate ||
            (!slot.specific_date && slot.day_of_week === weekday)
        )
        .sort((a, b) => a.start_time.localeCompare(b.start_time));
    },
  },
  actions: {
    async fetchSlots(filters = {}) {
      this.loading = true;
      try {
        const params = Object.fromEntries(
          Object.entries(filters).filter(([, value]) => value !== "" && value !== null && value !== undefined)
        );
        const { data } = await listSlots(params);
        this.items = data.slots;
      } finally {
        this.loading = false;
      }
    },
    async createSlot(payload) {
      const { data } = await createSlotRequest(payload);
      this.items.push(data.slot);
      return data.slot;
    },
    async updateSlot(id, payload) {
      const { data } = await updateSlotRequest(id, payload);
      this.items = this.items.map((slot) => (slot.id === id ? data.slot : slot));
      return data.slot;
    },
    async deleteSlot(id) {
      await deleteSlotRequest(id);
      this.items = this.items.filter((slot) => slot.id !== id);
    },
    async previewDay(payload) {
      const { data } = await autoScheduleRequest({ ...payload });
      return data;
    },
    async applyDay(payload) {
      const { data } = await autoScheduleRequest({ ...payload, apply: true });
      if (data.created?.length) {
        await this.fetchSlots();
      }
      return data;
    },
    async applyTemplate(payload) {
      const { data } = await applyTemplateRequest(payload);
      await this.fetchSlots();
      return data;
    },
    async fetchAvailableTemplates() {
      // Falls back to the built-in catalogue if the endpoint is unreachable,
      // so the picker never renders empty on older backends.
      try {
        const { data } = await listAvailableTemplatesRequest();
        this.availableTemplates = data.templates || [];
      } catch {
        this.availableTemplates = TEMPLATES.map((value) => ({
          value,
          name: value,
          label: value,
        }));
      }
      return this.availableTemplates;
    },
  },
});
