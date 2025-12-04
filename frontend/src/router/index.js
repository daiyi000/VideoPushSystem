import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '../store/user'; // 引入 Store 以获取用户信息
import MainLayout from '../layout/MainLayout.vue';

import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Upload from '../views/Upload.vue';
import Detail from '../views/Detail.vue';
import Profile from '../views/Profile.vue';
import Channel from '../views/Channel.vue';

import AdminLayout from '../views/admin/AdminLayout.vue';
import Dashboard from '../views/admin/Dashboard.vue';
import VideoManage from '../views/admin/VideoManage.vue';
import UserManage from '../views/admin/UserManage.vue';
import { ElMessage } from 'element-plus';
import NotFound from '../views/NotFound.vue';
import VideoAudit from '../views/admin/VideoAudit.vue';
const routes = [
  { path: '/login', name: 'Login', component: Login },
  
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
  },

  // 后台管理路由
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAdmin: true }, // 【标记】需要管理员权限
    children: [
      { path: 'dashboard', component: Dashboard },
      { path: 'videos', component: VideoManage },
      { path: 'users', component: UserManage },
      { path: 'audit/:id', component: VideoAudit } 
    ]
  },
  { path: '/:pathMatch(.*)*', 
    name: 'NotFound', 
    component: NotFound 
  },

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 【核心】路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  
  // 检查目标路由是否需要管理员权限
  if (to.meta.requiresAdmin) {
    // 1. 未登录 -> 去登录
    if (!userStore.token) {
      ElMessage.warning('请先登录管理员账号');
      next('/login');
    } 
    // 2. 已登录但不是管理员 -> 回首页
    else if (!userStore.userInfo.is_admin) {
      ElMessage.error('无权访问后台管理系统');
      next('/');
    } 
    // 3. 验证通过 -> 放行
    else {
      next();
    }
  } else {
    // 不需要权限的页面直接放行
    next();
  }
});

export default router;