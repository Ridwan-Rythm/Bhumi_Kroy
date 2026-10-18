import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Contract section 4: Vite proxies /api and /demo to the backend on port 8000.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
      "/demo": "http://localhost:8000",
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    css: false,
    env: { VITE_USE_MOCK: "1" }, // page tests run against the saved fixtures in src/mocks
  },
});
