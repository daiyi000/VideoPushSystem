import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia' // 引入 Pinia
import router from './router'       // 引入 Router
import App from './App.vue'

const app = createApp(App)

app.use(ElementPlus)
app.use(createPinia()) // 注册
app.use(router)        // 注册

app.mount('#app')