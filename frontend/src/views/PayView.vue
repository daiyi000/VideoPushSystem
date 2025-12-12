<template>
  <div class="pay-center">
    <h1>申请认证</h1>
    <div class="plans">
      <div class="plan-card" :class="{ active: selected === 1 }" @click="selected = 1">
        <div class="icon-box blue"><el-icon><Select /></el-icon></div>
        <h3>个人认证</h3>
        <p class="price">¥ 0.01 <span class="old">¥9.9</span></p>
        <ul><li>获得蓝色对勾徽章</li><li>身份标识</li></ul>
      </div>

      <div class="plan-card" :class="{ active: selected === 2 }" @click="selected = 2">
        <div class="icon-box yellow"><el-icon><Headset /></el-icon></div>
        <h3>音乐人认证</h3>
        <p class="price">¥ 0.02 <span class="old">¥19.9</span></p>
        <ul><li>获得黄色音符徽章</li><li>专属音乐区流量</li></ul>
      </div>
    </div>

    <el-button type="primary" size="large" round class="pay-btn" @click="handlePay" :loading="loading">
      立即支付 (支付宝沙盒)
    </el-button>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'; // 【修改】引入 watch
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
import request from '../api/request'; 
import { getProfile } from '../api/user';
import { ElMessage } from 'element-plus';
import { Select, Headset } from '@element-plus/icons-vue';

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);

// 缓存 Key 定义
const PENDING_ORDER_KEY = 'pending_pay_order';
const SELECTED_TYPE_KEY = 'pay_selected_type'; // 【新增】用于记忆选择的Key

// 【核心修改 1】初始化时，优先从 SessionStorage 读取上次的选择
const savedType = sessionStorage.getItem(SELECTED_TYPE_KEY);
const selected = ref(savedType ? Number(savedType) : 1);

// 【核心修改 2】监听 selected 变化，一旦用户切换，立刻存入缓存
watch(selected, (newVal) => {
  sessionStorage.setItem(SELECTED_TYPE_KEY, newVal);
});

// --- 查单逻辑 (保持不变) ---
const checkPaymentStatus = async () => {
  const pendingOrderNo = sessionStorage.getItem(PENDING_ORDER_KEY);
  if (!pendingOrderNo) return;
  if (loading.value) return;
  
  loading.value = true;
  try {
    const res = await request.post('/pay/query', { order_no: pendingOrderNo });
    
    if (res.data.status === 'success') {
      ElMessage.success('检测到支付成功！权益已发放');
      const profileRes = await getProfile(userStore.userInfo.id);
      if (profileRes.data.code === 200) {
        userStore.setLoginState(userStore.token, profileRes.data.data);
      }
      sessionStorage.removeItem(PENDING_ORDER_KEY);
      // 支付成功后，也可以选择清除记忆的选择，或者保留供下次使用，这里保留
      router.replace('/profile');
    } else {
      ElMessage.warning('支付未完成或已取消');
      sessionStorage.removeItem(PENDING_ORDER_KEY);
    }
  } catch (e) {
    console.error(e);
    sessionStorage.removeItem(PENDING_ORDER_KEY);
  } finally {
    loading.value = false;
  }
};

const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    checkPaymentStatus();
  }
};

onMounted(() => {
  checkPaymentStatus();
  document.addEventListener('visibilitychange', handleVisibilityChange);
});

onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange);
});

const handlePay = async () => {
  loading.value = true;
  try {
    const res = await request.post('/pay/create', {
      user_id: userStore.userInfo.id,
      ver_type: selected.value
    });

    if (res.data.code === 200) {
      sessionStorage.setItem(PENDING_ORDER_KEY, res.data.order_no);
      window.location.href = res.data.pay_url;
    }
  } catch (e) {
    console.error(e);
    ElMessage.error('发起支付失败');
    loading.value = false;
  }
};
</script>

<style scoped>
.pay-center { max-width: 800px; margin: 40px auto; text-align: center; }
.plans { display: flex; justify-content: center; gap: 20px; margin: 40px 0; }
.plan-card { 
  border: 2px solid #eee; border-radius: 12px; padding: 30px; width: 200px; cursor: pointer; transition: all 0.2s;
}
.plan-card:hover, .plan-card.active { border-color: #0f0f0f; transform: translateY(-5px); }
.icon-box { width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; color: white; font-size: 24px; }
.blue { background: #409EFF; }
.yellow { background: #E6A23C; }
.price { font-size: 24px; font-weight: bold; margin: 10px 0; }
.old { font-size: 14px; color: #999; text-decoration: line-through; font-weight: normal; }
.pay-btn { width: 200px; }
ul { list-style: none; padding: 0; color: #666; font-size: 14px; text-align: left; margin-top: 20px; }
li { margin-bottom: 8px; }
li::before { content: "✓"; margin-right: 5px; color: green; }
</style>