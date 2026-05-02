/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter",
          "Noto Sans Arabic",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "sans-serif",
        ],
      },
      colors: {
        brand: {
          DEFAULT: "#3B82F6",
          hover: "#2563EB",
        },
        accent: {
          DEFAULT: "#F59E0B",
          hover: "#D97706",
        },
      },
    },
  },
  plugins: [],
};
