import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/main.css' // 【核心修改】引入统一 CSS
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

const app = createApp(App)

app.use(ElementPlus)
app.use(createPinia()) // 注册
app.use(router)        // 注册

app.mount('#app')