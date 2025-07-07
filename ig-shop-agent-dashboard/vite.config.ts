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
    // Optimize build output for Azure Static Web Apps
    rollupOptions: {
      output: {
        // CRITICAL: Force new file names with timestamp for cache busting
        manualChunks: undefined,
        chunkFileNames: `assets/[name]-${Date.now()}-[hash].js`,
        entryFileNames: `assets/[name]-${Date.now()}-[hash].js`,
        assetFileNames: `assets/[name]-${Date.now()}-[hash].[ext]`
      }
    },
    // Minimize CSS and JS
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: false, // Keep console logs for debugging
        drop_debugger: true
      }
    },
    // Clear build cache
    emptyOutDir: true,
  },
  // Clear dev cache
  cacheDir: '.vite-cache-cleared',
})

