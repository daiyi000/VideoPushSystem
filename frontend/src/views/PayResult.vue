<template>
  <div class="result-container">
    <el-card class="result-card">
      <div v-if="status === 'loading'" class="status-box">
        <el-icon class="is-loading" size="50" color="#409EFF"><Loading /></el-icon>
        <h3>正在确认支付结果...</h3>
        <p>请稍候，不要关闭页面</p>
      </div>

      <div v-else-if="status === 'success'" class="status-box">
        <el-icon size="60" color="#67C23A"><CircleCheckFilled /></el-icon>
        <h2 class="success-title">认证成功！</h2>
        <p>权益已发放，{{ countdown }}秒后返回个人中心</p>
        <el-button type="primary" @click="$router.replace('/profile')">立即返回</el-button>
      </div>

      <div v-else class="status-box">
        <el-icon size="60" color="#F56C6C"><CircleCloseFilled /></el-icon>
        
        <h3>支付未完成</h3>
        <p>我们尚未收到您的付款确认，可能是您取消了支付或网络延迟。</p>
        
        <div class="btn-group">
          <el-button type="primary" @click="$router.replace('/pay')">重新支付</el-button>
          
          <el-button @click="$router.replace('/profile')">返回个人中心</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { queryOrder } from '../api/pay'; 
import { getProfile } from '../api/user';
import { useUserStore } from '../store/user';
import { Loading, CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const status = ref('loading');
const countdown = ref(3);

onMounted(async () => {
  // 1. 获取支付宝回传的订单号 (参数名通常是 out_trade_no)
  const orderNo = route.query.out_trade_no;
  
  if (!orderNo) {
    status.value = 'error';
    return;
  }

  try {
    // 2. 主动查单
    const res = await queryOrder({ order_no: orderNo });
    
    if (res.data.status === 'success') {
      status.value = 'success';
      
      // 3. 支付成功，强制刷新最新的用户信息 (含认证状态)
      const profileRes = await getProfile(userStore.userInfo.id);
      if (profileRes.data.code === 200) {
        userStore.setLoginState(userStore.token, profileRes.data.data);
      }

      // 4. 倒计时跳转
      const timer = setInterval(() => {
        countdown.value--;
        if (countdown.value <= 0) {
          clearInterval(timer);
          router.replace('/profile');
        }
      }, 1000);
      
    } else {
      status.value = 'error';
    }
  } catch (e) {
    console.error(e);
    status.value = 'error';
  }
});
</script>

<style scoped>
.result-container {
  display: flex; justify-content: center; align-items: center;
  height: 80vh; background: #f5f7fa;
}
.result-card { width: 400px; padding: 40px 20px; text-align: center; border-radius: 12px; }
.status-box { display: flex; flex-direction: column; align-items: center; gap: 15px; }
.success-title { color: #303133; margin: 10px 0 0; }
p { color: #909399; font-size: 14px; margin-bottom: 20px; }
.btn-group {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}
</style>