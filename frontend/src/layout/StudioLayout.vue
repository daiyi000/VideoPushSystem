<template>
  <div class="studio-layout">
    <!-- 侧边栏 -->
    <aside class="studio-sidebar">
      <div class="logo-area" @click="$router.push('/')">
        <el-icon color="#FF0000" size="28"><VideoPlay /></el-icon>
        <span class="logo-text">工作室</span>
      </div>
      
      <div class="user-brief">
        <el-avatar :size="80" :src="userStore.userInfo.avatar" class="avatar" />
        <div class="channel-name">您的频道</div>
        <div class="user-name">{{ userStore.userInfo.username }}</div>
      </div>

      <nav class="nav-menu">
        <div 
          v-for="item in menuItems" 
          :key="item.path" 
          class="nav-item" 
          :class="{ active: $route.path.includes(item.path) }"
          @click="$router.push(item.path)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </div>
      </nav>
      
      <div class="bottom-area">
        <div class="nav-item exit" @click="$router.push(`/channel/${userStore.userInfo.id}`)">
          <el-icon><Back /></el-icon>
          <span>返回频道</span>
        </div>
      </div>
    </aside>

    <!-- 主内容 -->
    <main class="studio-content">
      <header class="studio-header">
        <div class="page-title">{{ currentPageTitle }}</div>
        <div class="header-right">
          <el-button type="primary" size="small" @click="$router.push('/upload')">创建</el-button>
          <el-avatar :size="32" :src="userStore.userInfo.avatar" />
        </div>
      </header>
      <div class="content-scroll">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStore } from '../store/user';
import { VideoPlay, Odometer, Files, TrendCharts, MagicStick, Back } from '@element-plus/icons-vue';

const route = useRoute();
const userStore = useUserStore();

const menuItems = [
  { label: '信息中心', path: '/studio/dashboard', icon: Odometer },
  { label: '内容', path: '/studio/content', icon: Files },
  { label: '数据分析', path: '/studio/analytics', icon: TrendCharts },
  { label: '自定义', path: '/studio/customization', icon: MagicStick },
];

const currentPageTitle = computed(() => {
  const item = menuItems.find(i => route.path.includes(i.path));
  return item ? item.label : '频道工作室';
});
</script>

<style scoped>
.studio-layout { display: flex; height: 100vh; background: #f9f9f9; }

/* 侧边栏 */
.studio-sidebar { width: 256px; background: #fff; border-right: 1px solid #e5e5e5; display: flex; flex-direction: column; flex-shrink: 0; }
.logo-area { height: 64px; display: flex; align-items: center; padding-left: 24px; cursor: pointer; gap: 5px; }
.logo-text { font-size: 18px; font-weight: bold; color: #0f0f0f; letter-spacing: -0.5px; }

.user-brief { display: flex; flex-direction: column; align-items: center; padding: 20px 0; border-bottom: 1px solid #f0f0f0; }
.avatar { margin-bottom: 10px; border: 1px solid #eee; }
.channel-name { font-size: 12px; color: #606060; font-weight: bold; margin-bottom: 4px; }
.user-name { font-size: 14px; color: #0f0f0f; }

.nav-menu { flex: 1; padding: 12px 0; }
.nav-item { display: flex; align-items: center; height: 48px; padding: 0 24px; cursor: pointer; color: #606060; border-left: 3px solid transparent; transition: background 0.1s; }
.nav-item:hover { background: #f4f4f4; color: #0f0f0f; }
.nav-item.active { border-left-color: #ff0000; background: #fdfdfd; color: #cc0000; font-weight: 500; }
.nav-item .el-icon { margin-right: 20px; font-size: 20px; }

.bottom-area { padding-bottom: 20px; border-top: 1px solid #f0f0f0; }
.nav-item.exit:hover { color: #065fd4; }

/* 主内容 */
.studio-content { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.studio-header { height: 64px; background: #fff; border-bottom: 1px solid #e5e5e5; display: flex; justify-content: space-between; align-items: center; padding: 0 24px; }
.page-title { font-size: 20px; font-weight: 500; color: #0f0f0f; }
.header-right { display: flex; align-items: center; gap: 15px; }
.content-scroll { flex: 1; overflow-y: auto; padding: 24px; }
</style>