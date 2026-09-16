import { defineStore } from "pinia";
import { showToast } from "../composables/toast";

const MODES = {
  focus: { id: "focus", label: "Study Sprint", duration: 25 * 60 },
  shortBreak: { id: "shortBreak", label: "Short Break", duration: 5 * 60 },
  longBreak: { id: "longBreak", label: "Long Break", duration: 15 * 60 },
};

let intervalId = null;
let lastTickSecond = null;

// Synthesized audio tick for final 10s countdown
const playTickTone = (freq = 880, vol = 0.15) => {
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;
    const audioCtx = new AudioContextClass();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    gain.gain.setValueAtTime(vol, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.08);
  } catch {
    // Audio policy ignore
  }
};

// Completion chime (triumphant chord)
const playAlarmTone = () => {
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;
    const audioCtx = new AudioContextClass();

    const notes = [587.33, 739.99, 880.0]; // D5, F#5, A5 chord
    notes.forEach((freq, i) => {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime + i * 0.08);
      gain.gain.setValueAtTime(0.2, audioCtx.currentTime + i * 0.08);
      gain.gain.exponentialRampToValueAtTime(0.005, audioCtx.currentTime + 1.2);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start(audioCtx.currentTime + i * 0.08);
      osc.stop(audioCtx.currentTime + 1.2);
    });
  } catch {
    // Audio policy ignore
  }
};

// Soft pre-end warning (two gentle beeps) — played once per session
const playWarningTone = () => {
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;
    const audioCtx = new AudioContextClass();
    [0, 0.22].forEach((delay) => {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(660, audioCtx.currentTime + delay);
      gain.gain.setValueAtTime(0.18, audioCtx.currentTime + delay);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + delay + 0.18);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start(audioCtx.currentTime + delay);
      osc.stop(audioCtx.currentTime + delay + 0.18);
    });
  } catch {
    // Audio policy ignore
  }
};

export const useTimerStore = defineStore("timer", {
  state: () => ({
    currentMode: "focus",
    totalSeconds: MODES.focus.duration,
    remainingSeconds: MODES.focus.duration,
    isRunning: false,
    targetEndTime: null,
    sessionsCompleted: 0,
    soundEnabled: localStorage.getItem("tasknova-timer-sound") !== "off",
    warningThreshold: Number(localStorage.getItem("tasknova-timer-warn") || 30),
    _warned: false,
  }),

  getters: {
    formattedTime: (state) => {
      const m = Math.floor(state.remainingSeconds / 60);
      const s = state.remainingSeconds % 60;
      return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    },
    progressPercentage: (state) => {
      if (state.totalSeconds === 0) return 0;
      return Math.min(100, Math.max(0, ((state.totalSeconds - state.remainingSeconds) / state.totalSeconds) * 100));
    },
    currentModeLabel: (state) => {
      return MODES[state.currentMode]?.label || "Study Sprint";
    },
    isEndingSoon: (state) => {
      return state.isRunning && state.remainingSeconds <= 15 && state.remainingSeconds > 0;
    },
    isUrgent: (state) => {
      return state.isRunning && state.remainingSeconds <= 10 && state.remainingSeconds > 0;
    },
    isCritical: (state) => {
      return state.isRunning && state.remainingSeconds <= 5 && state.remainingSeconds > 0;
    },
  },

  actions: {
    toggleSound() {
      this.soundEnabled = !this.soundEnabled;
      try {
        localStorage.setItem("tasknova-timer-sound", this.soundEnabled ? "on" : "off");
      } catch { /* ignore */ }
    },
    setWarningThreshold(sec) {
      this.warningThreshold = Number(sec) || 30;
      try {
        localStorage.setItem("tasknova-timer-warn", String(this.warningThreshold));
      } catch { /* ignore */ }
      this._warned = false;
    },
    start() {
      if (this.isRunning) return;

      this.isRunning = true;
      this.targetEndTime = Date.now() + this.remainingSeconds * 1000;
      lastTickSecond = null;
      // Re-arm warning if remaining is above threshold (fresh session / resume)
      if (this.remainingSeconds > this.warningThreshold) this._warned = false;

      if (intervalId) clearInterval(intervalId);

      intervalId = setInterval(() => {
        if (!this.targetEndTime) return;
        const diff = Math.round((this.targetEndTime - Date.now()) / 1000);

        if (diff > 0) {
          this.remainingSeconds = diff;
          if (!this.soundEnabled) return;
          // One-time soft warning when crossing the threshold
          if (!this._warned && diff <= this.warningThreshold && diff > 10) {
            this._warned = true;
            playWarningTone();
          }
          // Trigger audio tick when counting down below 10 seconds
          if (diff <= 10 && diff !== lastTickSecond) {
            lastTickSecond = diff;
            const pitch = diff <= 3 ? 1046.5 : diff <= 5 ? 987.77 : 880;
            playTickTone(pitch, 0.18);
          }
        } else {
          this.remainingSeconds = 0;
          this.onTimerCompleted();
        }
      }, 500);
    },

    pause() {
      if (!this.isRunning) return;

      if (this.targetEndTime) {
        this.remainingSeconds = Math.max(0, Math.round((this.targetEndTime - Date.now()) / 1000));
      }

      this.isRunning = false;
      this.targetEndTime = null;
      lastTickSecond = null;

      if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
      }
    },

    reset() {
      this.pause();
      const mode = MODES[this.currentMode] || MODES.focus;
      this.remainingSeconds = mode.duration;
      this.totalSeconds = mode.duration;
      this._warned = false;
    },

    selectMode(modeId) {
      this.pause();
      const mode = MODES[modeId] || MODES.focus;
      this.currentMode = mode.id;
      this.totalSeconds = mode.duration;
      this.remainingSeconds = mode.duration;
      this._warned = false;
    },

    onTimerCompleted() {
      this.pause();
      if (this.soundEnabled) playAlarmTone();
      this._warned = false;

      if (this.currentMode === "focus") {
        this.sessionsCompleted += 1;
        showToast("Study sprint completed! Time for a short break.");
        this.selectMode("shortBreak");
      } else {
        showToast("Break is over! Ready for the next study sprint.");
        this.selectMode("focus");
      }
    },
  },
});
