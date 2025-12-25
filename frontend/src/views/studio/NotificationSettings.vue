<template>
  <div class="settings-container">
    <h2 class="page-title">通知设置</h2>
    <div class="settings-card">
      <div class="setting-group">
        <h3>通用通知</h3>
        <p class="desc">选择您希望收到的通知类型。</p>
        
        <div class="setting-item">
          <div class="label-box">
            <span class="label">订阅</span>
            <span class="sub-label">我订阅的频道有新动态时通知我</span>
          </div>
          <el-switch v-model="settings.notify_subscription" @change="updateSetting" />
        </div>

        <div class="setting-item">
          <div class="label-box">
            <span class="label">推荐视频</span>
            <span class="sub-label">根据我看过的视频，推荐我可能感兴趣的内容</span>
          </div>
          <el-switch v-model="settings.notify_recommendation" @change="updateSetting" />
        </div>
      </div>

      <el-divider />

      <div class="setting-group">
        <h3>互动与活动</h3>
        
        <div class="setting-item">
          <div class="label-box">
            <span class="label">我的频道互动</span>
            <span class="sub-label">我的频道或视频有新评论或其他互动时通知我</span>
          </div>
          <el-switch v-model="settings.notify_interaction" @change="updateSetting" />
        </div>

        <div class="setting-item">
          <div class="label-box">
            <span class="label">与我的评论有关的活动</span>
            <span class="sub-label">当我的评论有回复、点赞或其他相关活动时通知我</span>
          </div>
          <el-switch v-model="settings.notify_comment" @change="updateSetting" />
        </div>

        <div class="setting-item">
          <div class="label-box">
            <span class="label">@ 我</span>
            <span class="sub-label">有人 @ 我的频道时通知��</span>
          </div>
          <el-switch v-model="settings.notify_mention" @change="updateSetting" />
        </div>
      </div>
      
      <el-divider />
      
      <div class="setting-group">
         <h3>其他</h3>
         <div class="setting-item">
          <div class="label-box">
            <span class="label">促销内容和优惠活动</span>
            <span class="sub-label">向我发送促销内容和优惠活动信息</span>
          </div>
          <el-switch v-model="settings.notify_promotion" @change="updateSetting" />
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../../store/user';
import request from '../../api/request';
import { ElMessage } from 'element-plus';

const userStore = useUserStore();
const settings = ref({
  notify_subscription: true,
  notify_recommendation: true,
  notify_interaction: true,
  notify_comment: true,
  notify_mention: true,
  notify_promotion: true,
  notify_system: true
});

const loadSettings = async () => {
  if(!userStore.token) return;
  try {
    const res = await request.get(`/notification/settings?user_id=${userStore.userInfo.id}`);
    if(res.data.code === 200) {
       settings.value = res.data.data;
    }
  } catch(e) { console.error(e); }
};

const updateSetting = async () => {
  try {
    await request.post('/notification/settings', {
       user_id: userStore.userInfo.id,
       ...settings.value
    });
    ElMessage.success('设置已保存');
  } catch(e) { 
    ElMessage.error('保存失败');
  }
};

onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
.settings-container { max-width: 800px; margin: 30px auto; padding: 0 20px; }
.page-title { margin-bottom: 20px; font-size: 24px; color: #0f0f0f; }
.settings-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.setting-group h3 { margin-bottom: 10px; font-size: 18px; color: #0f0f0f; }
.desc { color: #606060; font-size: 14px; margin-bottom: 20px; }
.setting-item { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; }
.label-box { display: flex; flex-direction: column; gap: 4px; }
.label { font-size: 16px; font-weight: 500; color: #0f0f0f; }
.sub-label { font-size: 13px; color: #606060; }
</style>