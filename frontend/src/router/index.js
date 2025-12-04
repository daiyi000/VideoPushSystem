import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '../layout/MainLayout.vue';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Upload from '../views/Upload.vue';
import Detail from '../views/Detail.vue';
import Profile from '../views/Profile.vue';
import Channel from '../views/Channel.vue';

const routes = [
  // 登录页不需要布局，独立出来
  { path: '/login', name: 'Login', component: Login },
  
  // 其他页面都使用 MainLayout
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', name: 'Home', component: Home },
      { path: 'upload', name: 'Upload', component: Upload },
      { path: 'video/:id', name: 'Detail', component: Detail },
      { path: 'profile', name: 'Profile', component: Profile },
      { path: 'channel/:id', name: 'Channel', component: Channel }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(), // 使用 HTML5 模式
  routes
});

export default router;