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
          <button @click="handleSearch" title="搜索">
            <el-icon size="20" color="#333"><Search /></el-icon>
          </button>
        </div>
      </div>

      <div class="header-right">
        <div class="icon-btn-wrapper" @click="$router.push('/upload')" title="创建">
           <el-icon size="24"><VideoCamera /></el-icon>
        </div>
        
        <div v-if="!userStore.token" style="margin-left:15px">
          <el-button type="primary" round plain @click="$router.push('/login')">
             <el-icon style="margin-right:4px"><User /></el-icon> 登录
          </el-button>
        </div>
        
        <el-dropdown v-else trigger="click" @command="handleCommand" style="margin-left:15px">
          <el-avatar :size="32" :src="userStore.userInfo.avatar" style="cursor:pointer" />
          <template #dropdown>
            <el-dropdown-menu>
              <div style="padding:10px;text-align:center;font-weight:bold;border-bottom:1px solid #eee">
                {{ userStore.userInfo.username }}
              </div>
              <el-dropdown-item v-if="userStore.userInfo.is_admin" command="admin" style="color: #E6A23C; font-weight: bold;">
                <el-icon><Monitor /></el-icon> 后台管理
              </el-dropdown-item>
              <el-dropdown-item command="channel"><el-icon><User /></el-icon> 我的频道</el-dropdown-item>
              <el-dropdown-item command="studio"><el-icon><VideoPlay /></el-icon> 创作者工作室</el-dropdown-item>
              <el-dropdown-item command="profile"><el-icon><Collection /></el-icon> 历史与收藏</el-dropdown-item>
              <el-dropdown-item command="logout" divided><el-icon><SwitchButton /></el-icon> 退出登录</el-dropdown-item>
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
          <div class="nav-item" :class="{ active: $route.path.includes('/shorts') }" @click="goToShorts">
            <el-icon><Film /></el-icon>
            <span>Shorts</span>
          </div>
          <div class="nav-item" :class="{ active: $route.path === '/profile' }" @click="$router.push('/profile')">
            <el-icon><Collection /></el-icon>
            <span>历史与收藏</span>
          </div>
        </div>
        <el-divider style="margin: 10px 0" />
        <div class="nav-section" v-if="userStore.token">
          <div class="section-title" v-if="!isCollapsed">订阅列表</div>
          <div v-for="user in followingList" :key="user.id" class="nav-item user-item" @click="$router.push(`/@${user.username}`)">
            <el-avatar :size="24" :src="user.avatar" />
            <span class="username">{{ user.username }}</span>
          </div>
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
import { Menu, VideoPlay, Search, VideoCamera, HomeFilled, Collection, Monitor, Film, User, SwitchButton, Clock, Star } from '@element-plus/icons-vue';

const router = useRouter();
const userStore = useUserStore();
const isCollapsed = ref(false);
const keyword = ref('');
const followingList = ref([]);

const toggleSidebar = () => { isCollapsed.value = !isCollapsed.value; };
const handleSearch = () => { if (keyword.value.trim()) { router.push(`/?q=${keyword.value}&t=${Date.now()}`); } };
const goToShorts = () => { router.push('/shorts/random'); };
const handleCommand = (cmd) => {
  if (cmd === 'logout') { userStore.logout(); router.push('/login'); }
  if (cmd === 'profile') router.push('/profile');
  if (cmd === 'channel') router.push(`/@${userStore.userInfo.username}`);
  if (cmd === 'studio') router.push('/studio/dashboard');
  if (cmd === 'admin') router.push('/admin/dashboard');
};
const fetchFollowing = async () => {
  if (!userStore.token) return;
  try {
    const res = await request.get(`/user/following_list?user_id=${userStore.userInfo.id}`);
    if (res.data.code === 200) followingList.value = res.data.data;
  } catch (e) { console.error(e); }
};
onMounted(() => { fetchFollowing(); });
</script>

<style scoped>
.app-layout { height: 100vh; display: flex; flex-direction: column; }

/* Header - 透明毛玻璃核心 */
.app-header {
  height: 56px; 
  /* 90% 不透明的白色，确保能看到后面滚动的视频 */
  background: rgba(255, 255, 255, 0.9);
  /* 强力模糊效果 */
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  
  display: flex; justify-content: space-between; align-items: center; 
  padding: 0 16px; 
  position: fixed; 
  top: 0; left: 0; right: 0; 
  z-index: 2020;
  /* 只有极淡的边框，增强融合感 */
  border-bottom: 1px solid rgba(0,0,0,0.05); 
}

/* 布局调整：让内容能滚到 header 后面 */
.app-body { 
  display: flex; 
  margin-top: 0; /* 【关键】取消之前的 56px 边距 */
  height: 100vh; /* 占满全屏 */
  width: 100%;
}

/* Sidebar */
.app-sidebar { 
  width: 240px; 
  background: #fff; 
  overflow-y: auto; 
  padding: 12px; 
  padding-top: 68px; /* 【关键】顶部留出空间，因为 header 盖在上面 */
  transition: width 0.2s; 
  display: flex; flex-direction: column; 
  scrollbar-width: thin;
  z-index: 1010; /* 比 header 低，但在内容之上 */
  border-right: 1px solid rgba(0,0,0,0.05);
}
.app-sidebar.collapsed { width: 72px; padding: 12px 4px; padding-top: 68px; }

/* Content */
.app-content { 
  flex: 1; 
  overflow-y: auto; /* 允许内部滚动 */
  background: #fff; 
  padding: 0; /* 这里的 padding 交给子页面控制，或者统一这里设 */
  padding-top: 56px; /* 【关键】内容初始位置下移，避免被 header 挡住 */
  /* 当你滚动 .app-content 时，内容会往上走，header 是 fixed 的，所以内容会穿过 header */
}

/* 其他样式保持不变 */
.header-left { display: flex; align-items: center; gap: 16px; }
.logo { display: flex; align-items: center; font-weight: bold; font-size: 18px; cursor: pointer; letter-spacing: -0.5px; color: #212121; font-family: "YouTube Sans", Roboto, sans-serif; }
.menu-btn { color: #030303; padding: 8px; border-radius: 50%; }
.menu-btn:hover { background: #e5e5e5; }
.header-center { flex: 1; display: flex; justify-content: center; max-width: 720px; margin-left: 40px; }
.search-box { display: flex; width: 100%; align-items: center; }
.search-box input { flex: 1; height: 40px; padding: 0 16px; font-size: 16px; color: hsl(0,0%,6.7%); background-color: rgba(255,255,255,0.8); /* 搜索框也微透 */ border: 1px solid #ccc; border-right: none; border-radius: 20px 0 0 20px; outline: none; box-shadow: inset 0 1px 2px #eee; }
.search-box input:focus { border-color: #1c62b9; box-shadow: inset 0 1px 2px #eee; }
.search-box button { width: 64px; height: 40px; border: 1px solid #d3d3d3; background-color: #f8f8f8; border-radius: 0 20px 20px 0; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background-color 0.2s; }
.search-box button:hover { background-color: #f0f0f0; border-color: #c6c6c6; box-shadow: 0 1px 0 rgba(0,0,0,0.1); }
.header-right { display: flex; align-items: center; gap: 8px; }
.icon-btn-wrapper { width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 50%; cursor: pointer; color: #030303; }
.icon-btn-wrapper:hover { background: #e5e5e5; }

.nav-item { display: flex; align-items: center; padding: 0 12px; height: 40px; border-radius: 10px; cursor: pointer; color: #0f0f0f; margin-bottom: 4px; }
.nav-item:hover { background: #f2f2f2; }
.nav-item.active { background: #f2f2f2; font-weight: 500; }
.nav-item .el-icon { font-size: 24px; margin-right: 24px; color: #030303; }
.nav-item span { font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.app-sidebar.collapsed .nav-item { flex-direction: column; justify-content: center; height: 74px; padding: 16px 0 14px 0; gap: 6px; margin-bottom: 0; border-radius: 10px; }
.app-sidebar.collapsed .nav-item .el-icon { margin-right: 0; margin-bottom: 0; }
.app-sidebar.collapsed .nav-item span { font-size: 10px; line-height: 14px; }
.app-sidebar.collapsed .section-title, .app-sidebar.collapsed .username, .app-sidebar.collapsed .empty-tip, .app-sidebar.collapsed .login-tip { display: none; }
.app-sidebar.collapsed .user-item { justify-content: center; padding: 10px 0; }
.section-title { padding: 6px 12px; font-size: 16px; font-weight: bold; margin-top: 6px; color: #0f0f0f; }
.user-item { gap: 12px; }
.username { font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.empty-tip, .login-tip { padding: 12px; font-size: 13px; color: #606060; line-height: 1.5; }
</style>