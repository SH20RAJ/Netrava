/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#080B11",
        surface: "#0F1623",
        "surface-raised": "#162032",
        "surface-border": "#1E2C42",
        "police-gold": "#F59E0B",
        "alert-red": "#EF4444",
        "alert-amber": "#F97316",
        "telemetry-green": "#10B981",
        "cyber-cyan": "#06B6D4",
        "tactical-blue": "#3B82F6",
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      },
    },
  },
  plugins: [],
};
