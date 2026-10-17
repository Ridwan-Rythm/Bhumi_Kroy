/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Noto Sans Bengali"', "system-ui", "sans-serif"],
      },
      minHeight: { tap: "44px" },
      minWidth: { tap: "44px" },
      colors: {
        // verdict colours; never used alone (icon + word + colour, see rule 6)
        verdict: {
          green: "#1b6e3c",
          grey: "#4b5563",
          amber: "#8a5a00",
          red: "#a61b1b",
          integrity: "#5b21b6",
        },
      },
    },
  },
  plugins: [],
};
