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
  },
  
  // 【新增】本地开发服务器配置
  server: {
    // 端口号 (可选，默认就是 5173)
    port: 5173,
    // 代理配置：解决本地开发时的跨域问题
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // 本地后端的地址
        changeOrigin: true,
        // 如果你的后端接口不带 /api 前缀，需要把 /api 去掉，
        // 但根据你的 request.js，你后端路由应该就是带 /api 的，所以通常不需要 rewrite
        // rewrite: (path) => path.replace(/^\/api/, '') 
      },
      '/static': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})