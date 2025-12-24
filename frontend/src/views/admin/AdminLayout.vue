<template>
  <div class="apple-admin-container">
    <!-- Top Navigation Bar -->
    <header class="apple-nav">
      <div class="nav-content">
        <div class="nav-left">
          <div class="apple-logo-text">VideoPush <span class="thin">Admin</span></div>
          <nav class="nav-links">
            <router-link to="/admin/dashboard" class="nav-item" active-class="active">Dashboard</router-link>
            <router-link to="/admin/videos" class="nav-item" active-class="active">Videos</router-link>
            <router-link to="/admin/users" class="nav-item" active-class="active">Users</router-link>
          </nav>
        </div>
        <div class="nav-right">
          <span class="back-link" @click="$router.push('/')">Exit to App</span>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="apple-main">
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Global Layout */
.apple-admin-container {
  min-height: 100vh;
  background-color: #F5F5F7; /* Apple System Gray 6 */
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* Navigation Bar */
.apple-nav {
  background-color: #1C1C1E; /* Dark background */
  height: 48px;
  width: 100%;
  display: flex;
  justify-content: center;
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(20px);
  background-color: rgba(28, 28, 30, 0.85); /* Translucent dark */
}

.nav-content {
  width: 100%;
  max-width: 1200px; /* Content width constraint */
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 40px;
}

.apple-logo-text {
  color: #fff;
  font-size: 19px;
  font-weight: 600;
  letter-spacing: -0.5px;
  cursor: default;
}

.apple-logo-text .thin {
  font-weight: 300;
  color: #A1A1A6;
}

.nav-links {
  display: flex;
  gap: 24px;
}

.nav-item {
  color: #A1A1A6;
  text-decoration: none;
  font-size: 13px;
  font-weight: 400;
  transition: color 0.2s;
}

.nav-item:hover {
  color: #fff;
}

.nav-item.active {
  color: #fff;
  font-weight: 500;
}

.nav-right {
  display: flex;
  align-items: center;
}

.back-link {
  color: #2997FF; /* Apple Blue */
  font-size: 12px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.back-link:hover {
  opacity: 0.8;
  text-decoration: underline;
}

/* Main Content */
.apple-main {
  padding: 40px 0;
  display: flex;
  justify-content: center;
}

.content-wrapper {
  width: 100%;
  max-width: 1200px;
  padding: 0 20px;
}
</style>

<style>
/* Global Overrides for Element Plus within Admin to match Apple Style */

/* Cards */
.apple-admin-container .el-card {
  border: 1px solid #D2D2D7;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
  background-color: #fff;
}

.apple-admin-container .el-card__header {
  border-bottom: 1px solid #E5E5E5;
  padding: 16px 24px;
  font-weight: 600;
  font-size: 17px;
  color: #1D1D1F;
}

.apple-admin-container .el-card__body {
  padding: 24px;
}

/* Tables */
.apple-admin-container .el-table {
  --el-table-header-bg-color: #fff;
  --el-table-row-hover-bg-color: #F5F5F7;
  --el-table-border-color: #E5E5E5;
  font-size: 13px;
}

.apple-admin-container .el-table th.el-table__cell {
  font-weight: 600;
  color: #86868B;
  border-bottom: 1px solid #E5E5E5 !important;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.5px;
}

/* Buttons */
.apple-admin-container .el-button--primary {
  background-color: #0071E3;
  border-color: #0071E3;
  border-radius: 980px; /* Pill shape */
  font-weight: 500;
}

.apple-admin-container .el-button--primary:hover {
  background-color: #0077ED;
  border-color: #0077ED;
}

.apple-admin-container .el-button--default {
  border-radius: 980px;
}
</style>