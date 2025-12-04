<template>
  <div class="admin-container">
    <div class="admin-sidebar">
      <div class="logo">VideoHub 后台</div>
      <div class="menu">
        <div class="menu-item" :class="{active: $route.path==='/admin/dashboard'}" @click="$router.push('/admin/dashboard')">
          数据大屏
        </div>
        <div class="menu-item" :class="{active: $route.path==='/admin/videos'}" @click="$router.push('/admin/videos')">
          视频管理
        </div>
        <div class="menu-item" :class="{active: $route.path==='/admin/users'}" @click="$router.push('/admin/users')">
          用户管理
        </div>
        <div class="menu-item exit" @click="$router.push('/')">
          返回前台
        </div>
      </div>
    </div>
    <div class="admin-content">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.admin-container { display: flex; height: 100vh; background: #f0f2f5; }
.admin-sidebar { width: 220px; background: #001529; color: white; display: flex; flex-direction: column; }
.logo { height: 60px; line-height: 60px; text-align: center; font-size: 20px; font-weight: bold; background: #002140; }
.menu { flex: 1; padding: 20px 0; }
.menu-item { padding: 15px 20px; cursor: pointer; transition: 0.3s; }
.menu-item:hover { background: #1890ff; }
.menu-item.active { background: #1890ff; }
.menu-item.exit { margin-top: 50px; background: #ff4d4f; }
.admin-content { flex: 1; padding: 20px; overflow-y: auto; }
</style>