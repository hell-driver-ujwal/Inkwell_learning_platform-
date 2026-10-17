/** Keep browser requests same-origin so Django session cookies and CSRF work naturally. */
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
const apiTarget = process.env.API_PROXY_TARGET || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/robots.txt": apiTarget,
      "/sitemap.xml": apiTarget,
      "/api": apiTarget,
      "/django-admin": apiTarget,
    },
  },
});
