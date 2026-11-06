import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// During development, Vite serves the UI on :5173 and forwards /api to FastAPI on :8000.
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
