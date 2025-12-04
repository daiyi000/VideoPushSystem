<template>
  <div class="not-found">
    <div class="content">
      <el-icon class="icon" color="#909399"><WarningFilled /></el-icon>
      <h1>404</h1>
      <p>视频不存在、已下架或正在审核中</p>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { WarningFilled } from '@element-plus/icons-vue';
</script>

<style scoped>
.not-found {
  height: 80vh;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}
.icon { font-size: 80px; margin-bottom: 20px; }
h1 { font-size: 60px; color: #303133; margin: 0; }
p { color: #606266; font-size: 18px; margin: 20px 0 30px; }
</style>