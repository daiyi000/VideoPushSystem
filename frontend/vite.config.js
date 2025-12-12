// frontend/vite.config.js
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // 这一行非常重要，它告诉 Vite "@" 符号代表 "src" 目录
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})