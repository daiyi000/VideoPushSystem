<template>
  <div class="app-layout">
    <!-- 1. 顶部导航栏 -->
    <header class="app-header">
      <div class="header-left">
        <el-button link @click="toggleSidebar" class="menu-btn">
          <el-icon size="24"><Menu /></el-icon>
        </el-button>
        <div class="logo" @click="$router.push('/')">
          <el-icon color="#FF0000" size="28" style="margin-right:5px"><VideoPlay /></el-icon>
          <span>VideoHub</span>
        </div>
      </div>

      <div class="header-center">
        <div class="search-box">
          <input v-model="keyword" placeholder="搜索" @keyup.enter="handleSearch" />
          <button @click="handleSearch"><el-icon><Search /></el-icon></button>
        </div>
      </div>

      <div class="header-right">
        <el-button link @click="$router.push('/upload')"><el-icon size="22"><VideoCamera /></el-icon></el-button>
        
        <div v-if="!userStore.token" style="margin-left:15px">
          <el-button type="primary" round plain @click="$router.push('/login')">登录</el-button>
        </div>
        
        <el-dropdown v-else trigger="click" @command="handleCommand" style="margin-left:15px">
          <el-avatar :size="32" :src="userStore.userInfo.avatar" style="cursor:pointer" />
          <template #dropdown>
            <el-dropdown-menu>
              <div style="padding:10px;text-align:center;font-weight:bold">{{ userStore.userInfo.username }}</div>
              
              <!-- 管理员入口 -->
              <el-dropdown-item v-if="userStore.userInfo.is_admin" command="admin" divided style="color: #E6A23C; font-weight: bold;">
                <el-icon><Monitor /></el-icon> 后台管理
              </el-dropdown-item>

              <el-dropdown-item command="profile" :divided="!userStore.userInfo.is_admin">个人中心</el-dropdown-item>
              <el-dropdown-item command="channel">我的频道</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div class="app-body">
      <!-- 2. 侧边栏 -->
      <aside class="app-sidebar" :class="{ 'collapsed': isCollapsed }">
        <div class="nav-section">
          <div class="nav-item" :class="{ active: $route.path === '/' }" @click="$router.push('/')">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </div>
          <div class="nav-item" @click="$router.push('/profile')">
            <el-icon><Collection /></el-icon>
            <span>历史与收藏</span>
          </div>
        </div>

        <el-divider style="margin: 10px 0" />

        <div class="nav-section" v-if="userStore.token">
          <div class="section-title" v-if="!isCollapsed">订阅内容</div>
          <!-- 【核心修复】侧边栏点击关注用户，跳转到 /@username -->
          <div v-for="user in followingList" :key="user.id" class="nav-item user-item" @click="$router.push(`/@${user.username}`)">
            <el-avatar :size="24" :src="user.avatar" />
            <span class="username">{{ user.username }}</span>
          </div>
          <div v-if="followingList.length === 0 && !isCollapsed" class="empty-tip">暂无关注</div>
        </div>
        
        <div v-if="!userStore.token && !isCollapsed" class="login-tip">
          登录后查看关注更新
        </div>
      </aside>

      <!-- 3. 主内容区 -->
      <main class="app-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
import request from '../api/request';
import { Menu, VideoPlay, Search, VideoCamera, HomeFilled, Collection, Monitor } from '@element-plus/icons-vue';

const router = useRouter();
const userStore = useUserStore();

const isCollapsed = ref(false);
const keyword = ref('');
const followingList = ref([]);

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const handleSearch = () => {
  router.push(`/?q=${keyword.value}&t=${Date.now()}`); 
};

const handleCommand = (cmd) => {
  if (cmd === 'logout') { userStore.logout(); router.push('/login'); }
  if (cmd === 'profile') router.push('/profile');
  // 【核心修复】下拉菜单跳转我的频道，使用 /@username
  if (cmd === 'channel') router.push(`/@${userStore.userInfo.username}`);
  if (cmd === 'admin') router.push('/admin/dashboard');
};

const fetchFollowing = async () => {
  if (!userStore.token) return;
  try {
    const res = await request.get(`/user/following_list?user_id=${userStore.userInfo.id}`);
    if (res.data.code === 200) {
      followingList.value = res.data.data;
    }
  } catch (e) { console.error(e); }
};

onMounted(() => {
  fetchFollowing();
});
</script>

<style scoped>
/* 样式保持不变 */
.app-layout { height: 100vh; display: flex; flex-direction: column; }

/* Header */
.app-header {
  height: 56px; background: white; display: flex; justify-content: space-between; align-items: center; padding: 0 16px; 
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.header-left { display: flex; align-items: center; gap: 16px; }
.logo { display: flex; align-items: center; font-weight: bold; font-size: 18px; cursor: pointer; letter-spacing: -0.5px; }
.menu-btn { color: #606060; }

.header-center { flex: 1; display: flex; justify-content: center; max-width: 700px; }
.search-box { display: flex; width: 100%; max-width: 600px; }
.search-box input { flex: 1; padding: 0 16px; border: 1px solid #ccc; border-radius: 20px 0 0 20px; height: 40px; outline: none; }
.search-box input:focus { border-color: #1c62b9; }
.search-box button { width: 64px; border: 1px solid #ccc; border-left: none; background: #f8f8f8; border-radius: 0 20px 20px 0; cursor: pointer; }

.header-right { display: flex; align-items: center; }

/* Body */
.app-body { display: flex; margin-top: 56px; height: calc(100vh - 56px); }

/* Sidebar */
.app-sidebar { width: 240px; background: white; overflow-y: auto; padding: 12px; transition: width 0.2s; display: flex; flex-direction: column; }
.app-sidebar.collapsed { width: 72px; padding: 12px 4px; }

/* Sidebar Items */
.nav-item { display: flex; align-items: center; padding: 0 12px; height: 48px; border-radius: 10px; cursor: pointer; color: #0f0f0f; }
.nav-item:hover { background: #f2f2f2; }
.nav-item.active { background: #f2f2f2; font-weight: 500; }
.nav-item .el-icon { font-size: 24px; margin-right: 20px; }
.nav-item span { font-size: 14px; white-space: nowrap; overflow: hidden; }

/* 折叠后样式 */
.app-sidebar.collapsed .nav-item { flex-direction: column; justify-content: center; height: 70px; padding: 0; gap: 5px; }
.app-sidebar.collapsed .nav-item .el-icon { margin-right: 0; margin-bottom: 4px; }
.app-sidebar.collapsed .nav-item span { font-size: 10px; }
.app-sidebar.collapsed .section-title, 
.app-sidebar.collapsed .username,
.app-sidebar.collapsed .empty-tip,
.app-sidebar.collapsed .login-tip { display: none; }
.app-sidebar.collapsed .user-item { justify-content: center; }

.section-title { padding: 8px 12px; font-size: 16px; font-weight: bold; margin-top: 10px; }
.user-item { gap: 15px; }
.username { font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.empty-tip, .login-tip { padding: 12px; font-size: 13px; color: #606060; }

.app-content { flex: 1; overflow-y: auto; background: #f9f9f9; padding: 24px; }
</style>