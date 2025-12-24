<template>
  <div class="forgot-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>找回密码</span>
        </div>
      </template>
      
      <p style="font-size: 13px; color: #606060; margin-bottom: 20px;">
        请输入您注册时使用的邮箱地址。我们将通知管理员审核您的重置请求。
      </p>

      <el-form :model="form" @submit.prevent="handleSubmit">
        <el-form-item>
          <el-input v-model="form.email" placeholder="请输入邮箱地址" prefix-icon="Message"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" style="width: 100%" @click="handleSubmit" :loading="loading">
            提交申请
          </el-button>
        </el-form-item>
        
        <div style="text-align: center;">
          <el-button link @click="$router.push('/login')">返回登录</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import request from '../api/request';
import { ElMessage } from 'element-plus';
import { Message } from '@element-plus/icons-vue';

const form = ref({ email: '' });
const loading = ref(false);

const handleSubmit = async () => {
  if (!form.value.email) return ElMessage.warning('请输入邮箱');
  
  loading.value = true;
  try {
    const res = await request.post('/auth/forgot_password', { email: form.value.email });
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg);
    } else {
      ElMessage.error(res.data.msg);
    }
  } catch (error) {
    if (error.response) {
       ElMessage.error(error.response.data.msg || '提交失败');
    } else {
       ElMessage.error('网络错误');
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.forgot-container { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #eef0f3; }
.box-card { width: 400px; }
.card-header { text-align: center; font-weight: bold; font-size: 18px; }
</style>