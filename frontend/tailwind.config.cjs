/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{vue,js}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
          950: "#1e1b4b",
        },
        ink: {
          DEFAULT: "#0F172A",
          light: "#334155",
          muted: "#64748B",
        },
        paper: {
          DEFAULT: "#F8FAFC",
          card: "#FFFFFF",
          muted: "#F1F5F9",
        },
        night: {
          bg: "#0B0F19",
          surface: "#111827",
          card: "#1E293B",
          cardHover: "#26334D",
          border: "#1E293B",
          borderSubtle: "#334155",
        },
        ledger: {
          green: "#059669",
          greenDark: "#10B981",
          greenLight: "#D1FAE5",
        },
        ember: {
          DEFAULT: "#E11D48",
          dark: "#F43F5E",
          light: "#FFE4E6",
        },
        academic: {
          purple: "#7C3AED",
          purpleLight: "#EDE9FE",
          blue: "#2563EB",
          blueLight: "#DBEAFE",
          teal: "#0D9488",
          tealLight: "#CCFBF1",
          amber: "#D97706",
          amberLight: "#FEF3C7",
        }
      },
      fontFamily: {
        display: ['"Outfit"', "sans-serif"],
        sans: ['"Plus Jakarta Sans"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
      boxShadow: {
        'glow-sm': '0 0 15px -3px rgba(99, 102, 241, 0.25)',
        'glow-md': '0 0 25px -5px rgba(99, 102, 241, 0.35)',
        'glow-success': '0 0 20px -5px rgba(16, 185, 129, 0.35)',
        'glow-urgent': '0 0 20px -5px rgba(244, 63, 94, 0.35)',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)',
        'card-hover': '0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04)',
        'card-dark': '0 4px 20px 0 rgba(0, 0, 0, 0.35)',
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.2s ease-out forwards',
        'slide-up': 'slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'scale-in': 'scaleIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'shimmer': 'shimmer 2s infinite linear',
        'spin-reverse': 'spinReverse 2.5s linear infinite',
        'bounce-dot': 'bounceDot 1.4s infinite ease-in-out both',
        'tick-pop': 'tickPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards',
        'pulse-urgent': 'pulseUrgent 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-warning': 'pulseWarning 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bar-rise': 'barRise 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.96)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        spinReverse: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(-360deg)' },
        },
        bounceDot: {
          '0%, 80%, 100%': { transform: 'scale(0)' },
          '40%': { transform: 'scale(1)' },
        },
        tickPop: {
          '0%': { transform: 'scale(1.15)', filter: 'brightness(1.25)' },
          '100%': { transform: 'scale(1)', filter: 'brightness(1)' },
        },
        pulseUrgent: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.88', transform: 'scale(1.02)' },
        },
        pulseWarning: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.88' },
        },
        barRise: {
          '0%': { transform: 'scaleY(0)', transformOrigin: 'bottom' },
          '100%': { transform: 'scaleY(1)', transformOrigin: 'bottom' },
        },
      },
      spacing: {
        "4.5": "1.125rem",
      },
    },
  },
  plugins: [],
};
