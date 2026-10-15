import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        night: { 950: "#060919", 900: "#0A0F27", 800: "#10163A", 700: "#1A2152" },
        indigo: { 400: "#8B93F5", 500: "#6770E6", 600: "#4A52C9" },
        violet: { 300: "#C4B0FF", 400: "#A68BFA", 500: "#8B5CF6", 600: "#7340E0" },
        gold: { 300: "#E6CB86", 400: "#D4AF5A", 500: "#C9A24B" },
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
