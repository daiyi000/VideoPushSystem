<template>
  <div class="reset-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>重置密码</span>
        </div>
      </template>
      
      <el-form :model="form" label-position="top">
        <el-form-item label="新密码">
          <el-input v-model="form.password" type="password" placeholder="请输入新密码" show-password></el-input>
        </el-form-item>
        
        <el-form-item label="确认密码">
          <el-input v-model="confirmPassword" type="password" placeholder="请再次输入新密码" show-password></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" style="width: 100%" @click="handleSubmit" :loading="loading">
            重置密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import request from '../api/request';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const token = ref('');
const form = ref({ password: '' });
const confirmPassword = ref('');
const loading = ref(false);

onMounted(() => {
  token.value = route.query.token;
  if (!token.value) {
    ElMessage.error('无效的链接');
  }
});

const handleSubmit = async () => {
  if (!token.value) return ElMessage.error('无效的令牌');
  if (!form.value.password) return ElMessage.warning('请输入新密码');
  if (form.value.password !== confirmPassword.value) return ElMessage.warning('两次密码不一致');
  
  loading.value = true;
  try {
    const res = await request.post('/auth/reset_password', { 
      token: token.value, 
      password: form.value.password 
    });
    
    if (res.data.code === 200) {
      ElMessage.success('重置成功，请登录');
      setTimeout(() => router.push('/login'), 1500);
    } else {
      ElMessage.error(res.data.msg);
    }
  } catch (error) {
    if (error.response) ElMessage.error(error.response.data.msg);
    else ElMessage.error('重置失败');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.reset-container { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #eef0f3; }
.box-card { width: 400px; }
.card-header { text-align: center; font-weight: bold; font-size: 18px; }
</style>