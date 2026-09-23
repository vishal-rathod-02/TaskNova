import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";
import "./style.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.mount("#app");

// Elegant boot-splash exit: fade + zoom out once the first route is ready,
// with a guaranteed minimum show time so refreshes always reveal the loader.
router.isReady().then(() => {
  requestAnimationFrame(() => {
    const splash = document.getElementById("boot-splash");
    if (!splash) return;
    const MIN_SHOW_MS = 1600; // always visible at least this long per load
    const elapsed = typeof performance !== "undefined" ? performance.now() : MIN_SHOW_MS;
    const wait = Math.max(0, MIN_SHOW_MS - elapsed);
    setTimeout(() => {
      splash.classList.add("boot-done");
      setTimeout(() => splash.remove(), 650);
    }, wait);
  });
});
