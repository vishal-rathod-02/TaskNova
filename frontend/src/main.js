import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";
import "./style.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.mount("#app");

// Elegant boot-splash exit: fade + zoom out once the first route is ready.
router.isReady().then(() => {
  requestAnimationFrame(() => {
    const splash = document.getElementById("boot-splash");
    if (!splash) return;
    // Let the first frame paint, then transition out.
    setTimeout(() => {
      splash.classList.add("boot-done");
      setTimeout(() => splash.remove(), 650);
    }, 350);
  });
});
