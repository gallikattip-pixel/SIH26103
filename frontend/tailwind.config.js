/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        infra: {
          bg: "#070c18",
          card: "#0d1527",
          cardHover: "#131e36",
          border: "#1e293b",
          borderLight: "#334155",
          cyan: "#06b6d4",
          teal: "#14b8a6",
          blue: "#3b82f6",
        },
        risk: {
          high: "#ef4444",
          highBg: "rgba(239, 68, 68, 0.12)",
          highBorder: "rgba(239, 68, 68, 0.3)",
          medium: "#f59e0b",
          mediumBg: "rgba(245, 158, 11, 0.12)",
          mediumBorder: "rgba(245, 158, 11, 0.3)",
          low: "#10b981",
          lowBg: "rgba(16, 185, 129, 0.12)",
          lowBorder: "rgba(16, 185, 129, 0.3)",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Menlo", "Consolas", "monospace"],
      },
      boxShadow: {
        "cyan-glow": "0 0 20px -5px rgba(6, 182, 212, 0.25)",
        "card-glow": "0 8px 24px -6px rgba(0, 0, 0, 0.45)",
      },
    },
  },
  plugins: [],
};
