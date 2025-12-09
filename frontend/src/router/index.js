import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '../store/user';
import { ElMessage } from 'element-plus';

// 布局组件
import MainLayout from '../layout/MainLayout.vue';
import AdminLayout from '../views/admin/AdminLayout.vue';
import StudioLayout from '../layout/StudioLayout.vue';

// 主站页面
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Upload from '../views/Upload.vue';
import Detail from '../views/Detail.vue';
import Profile from '../views/Profile.vue';
import Channel from '../views/Channel.vue';
import NotFound from '../views/NotFound.vue';

// 后台管理页面
import Dashboard from '../views/admin/Dashboard.vue';
import VideoManage from '../views/admin/VideoManage.vue';
import UserManage from '../views/admin/UserManage.vue';
import VideoAudit from '../views/admin/VideoAudit.vue';

// 创作者工作室页面
import StudioDashboard from '../views/studio/StudioDashboard.vue';
import StudioContent from '../views/studio/StudioContent.vue';
import StudioAnalytics from '../views/studio/StudioAnalytics.vue';
import StudioCustomization from '../views/studio/StudioCustomization.vue';

const routes = [
  // 登录页
  { path: '/login', name: 'Login', component: Login },
  
  // 主站路由 (使用 MainLayout)
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', name: 'Home', component: Home },
      { path: 'upload', name: 'Upload', component: Upload },
      { path: 'video/:id', name: 'Detail', component: Detail },
      { path: 'profile', name: 'Profile', component: Profile },
      // 原有的 ID 访问方式
      { path: 'channel/:id', name: 'Channel', component: Channel },
      // 【新增】支持 Handle 访问 (例如: /@bbcnewschinese)
      // 这将复用 Channel 组件，组件内需要处理 route.params.username
      { path: '@:username', name: 'ChannelHandle', component: Channel }
    ]
  },

  // 创作者工作室路由 (YouTube Studio 风格)
  {
    path: '/studio',
    component: StudioLayout,
    meta: { requiresAuth: true }, // 需要登录
    children: [
      { path: 'dashboard', component: StudioDashboard },
      { path: 'content', component: StudioContent },
      // 【修改】支持可选的 videoId 参数，用于区分频道整体分析和单个视频分析
      { path: 'analytics/:videoId?', component: StudioAnalytics },
      { path: 'customization', component: StudioCustomization },
      // 默认跳转到仪表盘
      { path: '', redirect: '/studio/dashboard' }
    ]
  },

  // 后台管理路由
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAdmin: true }, // 需要管理员权限
    children: [
      { path: 'dashboard', component: Dashboard },
      { path: 'videos', component: VideoManage },
      { path: 'users', component: UserManage },
      { path: 'audit/:id', component: VideoAudit } 
    ]
  },

  // 404 路由 (必须放在最后)
  { 
    path: '/:pathMatch(.*)*', 
    name: 'NotFound', 
    component: NotFound 
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 全局路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  
  // 1. 检查管理员权限
  if (to.meta.requiresAdmin) {
    if (!userStore.token) {
      ElMessage.warning('请先登录管理员账号');
      next('/login');
    } else if (!userStore.userInfo.is_admin) {
      ElMessage.error('无权访问后台管理系统');
      next('/');
    } else {
      next();
    }
  } 
  // 2. 检查普通登录权限 (如 Studio)
  else if (to.meta.requiresAuth) {
    if (!userStore.token) {
      ElMessage.warning('请先登录');
      next('/login');
    } else {
      next();
    }
  } 
  // 3. 公开页面放行
  else {
    next();
  }
});

export default router;