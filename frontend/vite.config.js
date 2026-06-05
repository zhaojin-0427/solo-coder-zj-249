import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 9701,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:9702',
        changeOrigin: true
      }
    }
  }
})
