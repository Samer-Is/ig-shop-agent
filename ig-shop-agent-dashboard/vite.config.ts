import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    // Disable source maps in production to reduce size
    sourcemap: false,
    // Set chunk size warning limit
    chunkSizeWarningLimit: 1000,
  },
})

