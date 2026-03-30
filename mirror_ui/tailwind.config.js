/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        divineo: {
          anthracite: "#141619",
          gold: "#C5A46D",
          bone: "#F5EFE6",
        },
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-out forwards",
      },
    },
  },
  plugins: [],
};
