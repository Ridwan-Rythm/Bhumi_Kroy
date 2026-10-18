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
        // brand palette (UI only): deep field green with a harvest-gold accent
        brand: {
          50: "#effaf3",
          100: "#d7f3e0",
          200: "#b0e6c4",
          300: "#7dd3a1",
          400: "#45b97b",
          500: "#229e61",
          600: "#167f4e",
          700: "#126541",
          800: "#115035",
          900: "#0d412c",
          950: "#052418",
        },
        gold: { 300: "#fbd97a", 400: "#f5c04a", 500: "#e8a920", 600: "#c88a10" },
        // verdict colours; never used alone (icon + word + colour, see rule 6)
        verdict: {
          green: "#1b6e3c",
          grey: "#4b5563",
          amber: "#8a5a00",
          red: "#a61b1b",
          integrity: "#5b21b6",
        },
      },
      boxShadow: {
        soft: "0 1px 2px rgb(16 24 40 / 0.04), 0 4px 16px -4px rgb(13 65 44 / 0.10)",
        lift: "0 2px 4px rgb(16 24 40 / 0.05), 0 16px 32px -8px rgb(13 65 44 / 0.22)",
        glow: "0 8px 28px -6px rgb(22 127 78 / 0.55)",
      },
      keyframes: {
        "fade-up": { "0%": { opacity: "0", transform: "translateY(14px)" }, "100%": { opacity: "1", transform: "none" } },
        "fade-in": { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        pop: { "0%": { opacity: "0", transform: "scale(0.94)" }, "60%": { transform: "scale(1.015)" }, "100%": { opacity: "1", transform: "none" } },
        float: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-10px)" } },
        drift: { "0%,100%": { transform: "translate(0,0) scale(1)" }, "50%": { transform: "translate(24px,-18px) scale(1.08)" } },
        shimmer: { "0%": { backgroundPosition: "-200% 0" }, "100%": { backgroundPosition: "200% 0" } },
        ping2: { "0%": { transform: "scale(0.8)", opacity: "0.7" }, "100%": { transform: "scale(2.2)", opacity: "0" } },
        scan: { "0%": { transform: "translateX(-100%)" }, "100%": { transform: "translateX(250%)" } },
        blink: { "0%,100%": { opacity: "0.25" }, "50%": { opacity: "1" } },
      },
      animation: {
        "fade-up": "fade-up .6s cubic-bezier(.2,.7,.2,1) both",
        "fade-in": "fade-in .5s ease both",
        pop: "pop .55s cubic-bezier(.2,.8,.2,1) both",
        float: "float 6s ease-in-out infinite",
        drift: "drift 14s ease-in-out infinite",
        shimmer: "shimmer 2.4s linear infinite",
        ping2: "ping2 2s cubic-bezier(0,0,.2,1) infinite",
        scan: "scan 1.8s ease-in-out infinite",
        blink: "blink 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
