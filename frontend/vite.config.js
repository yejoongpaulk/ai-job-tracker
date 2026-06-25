import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // Intercepts any request starting with /auth or /jobs
      '/auth': {
        target: 'http://127.0.0.1:8000', // Points directly to your FastAPI server local port
        changeOrigin: true,
        secure: false,
      },
      '/jobs': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
