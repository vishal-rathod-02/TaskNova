/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{vue,js}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ink: "#1B2A4A",
        paper: "#F2F4F6",
        amber: "#E8A33D",
        ledger: {
          green: "#2E6F5E",
          greenDark: "#4FA98D",
        },
        ember: {
          DEFAULT: "#E15B44",
          dark: "#F17A62",
        },
        slate: "#5B6472",
        night: {
          bg: "#10182B",
          surface: "#1B2438",
        },
      },
      fontFamily: {
        display: ["Newsreader", "Georgia", "serif"],
        sans: ['"IBM Plex Sans"', "Arial", "sans-serif"],
        mono: ['"IBM Plex Mono"', "monospace"],
      },
      spacing: {
        "4.5": "1.125rem",
      },
    },
  },
  plugins: [],
};
