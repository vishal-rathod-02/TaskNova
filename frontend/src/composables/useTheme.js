import { onMounted, ref, watch } from "vue";

const THEME_KEY = "tasknova_theme";

export function useTheme() {
  const isDark = ref(false);

  const applyTheme = () => {
    document.documentElement.classList.toggle("dark", isDark.value);
    localStorage.setItem(THEME_KEY, isDark.value ? "dark" : "light");
  };

  const toggleTheme = () => {
    isDark.value = !isDark.value;
  };

  onMounted(() => {
    isDark.value = localStorage.getItem(THEME_KEY) === "dark";
    applyTheme();
  });

  watch(isDark, applyTheme);

  return { isDark, toggleTheme };
}
