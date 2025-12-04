<template>
  <div class="login-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>{{ isRegister ? '注册新账号' : '登录系统' }}</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="70px">
        
        <!-- 邮箱输入框 -->
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱地址"></el-input>
        </el-form-item>

        <!-- 注册时显示验证码 -->
        <el-form-item label="验证码" v-if="isRegister">
          <div style="display: flex; gap: 10px;">
            <el-input v-model="form.code" placeholder="6位验证码" style="flex: 1"></el-input>
            <el-button 
              type="primary" 
              plain 
              :disabled="countdown > 0" 
              @click="handleSendCode"
            >
              {{ countdown > 0 ? `${countdown}s 后重试` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" style="width: 100%" @click="handleSubmit" :loading="loading">
            {{ isRegister ? '立即注册' : '立即登录' }}
          </el-button>
        </el-form-item>
        
        <div style="text-align: center;">
          <el-button link type="primary" @click="toggleMode">
            {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
import request from '../api/request'; 
import { login, register } from '../api/user';
import { ElMessage } from 'element-plus';

const router = useRouter();
const userStore = useUserStore();
const isRegister = ref(false);
const loading = ref(false);
const countdown = ref(0);

const form = ref({
  email: '',
  password: '',
  code: ''
});

const toggleMode = () => {
  isRegister.value = !isRegister.value;
  form.value = { email: '', password: '', code: '' };
  countdown.value = 0;
};

const handleSendCode = async () => {
  if (!form.value.email) return ElMessage.warning('请先填写邮箱');
  
  try {
    const res = await request.post('/auth/send_code', { email: form.value.email });
    if (res.data.code === 200) {
      ElMessage.success('验证码已发送，请查收邮件');
      countdown.value = 60;
      const timer = setInterval(() => {
        countdown.value--;
        if (countdown.value <= 0) clearInterval(timer);
      }, 1000);
    } else {
      ElMessage.error(res.data.msg);
    }
  } catch (error) {
    if (error.response && error.response.data && error.response.data.msg) {
        ElMessage.error(error.response.data.msg);
    } else {
        ElMessage.error('发送失败，请检查邮箱是否正确');
    }
  }
};

const handleSubmit = async () => {
  if (!form.value.email || !form.value.password) {
    return ElMessage.warning('邮箱和密码不能为空');
  }
  if (isRegister.value && !form.value.code) {
    return ElMessage.warning('请输入验证码');
  }

  loading.value = true;
  try {
    if (isRegister.value) {
      const res = await register(form.value);
      if (res.data.code === 200) {
        ElMessage.success('注册成功，请登录');
        isRegister.value = false;
      } else {
        ElMessage.error(res.data.msg);
      }
    } else {
      const res = await login(form.value);
      if (res.data.code === 200) {
        ElMessage.success('登录成功');
        userStore.setLoginState(res.data.data.token, res.data.data.user);
        router.push('/');
      } else {
        ElMessage.error(res.data.msg);
      }
    }
  } catch (error) {
    console.error(error);
    // 【核心修复】捕获 axios 抛出的 403 错误，并显示后端返回的 message
    if (error.response && error.response.data && error.response.data.msg) {
      ElMessage.error(error.response.data.msg);
    } else {
      ElMessage.error('网络请求失败');
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #eef0f3; }
.box-card { width: 400px; }
.card-header { text-align: center; font-weight: bold; font-size: 18px; }
</style>