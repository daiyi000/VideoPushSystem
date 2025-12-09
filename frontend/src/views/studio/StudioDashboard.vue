<template>
  <div class="dashboard-grid">
    <!-- 左列：最新视频 -->
    <div class="card video-snapshot" v-if="stats.recent_videos && stats.recent_videos.length > 0">
      <div class="card-header">最新视频表现</div>
      <div class="snapshot-content">
        <div class="thumb-box">
          <img :src="stats.recent_videos[0].cover_url" />
          <div class="v-title">{{ stats.recent_videos[0].title }}</div>
        </div>
        <div class="v-stats">
          <div class="stat-row">
            <el-icon><View /></el-icon>
            <span>{{ stats.recent_videos[0].views }} 次播放</span>
          </div>
          <div class="stat-row">
             <el-button link type="primary" @click="$router.push('/studio/analytics')">转到视频分析</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 右列：频道分析 -->
    <div class="card analytics-summary">
      <div class="card-header">频道分析</div>
      <div class="summary-body">
        <div class="big-stat">
          <div class="label">当前订阅者人数</div>
          <!-- 【修复】正确绑定 total_fans -->
          <div class="value">{{ stats.total_fans || 0 }}</div>
        </div>
        <el-divider />
        <div class="stat-summary">
          <div class="label">摘要</div>
          <div class="sub-label">历史累计数据</div>
          <div class="stat-row-simple">
            <span>观看次数</span>
            <span class="val">{{ stats.total_views }}</span>
          </div>
           <div class="stat-row-simple">
             <span>获赞次数</span>
             <!-- 【新增】展示获赞 -->
             <span class="val">{{ stats.total_likes }}</span>
          </div>
          <div class="stat-row-simple">
             <span>视频数量</span>
             <span class="val">{{ stats.total_videos }}</span>
          </div>
        </div>
        <div class="goto-analytics">
          <el-button type="primary" link @click="$router.push('/studio/analytics')">转到频道分析</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../../store/user';
import request from '../../api/request';
import { View } from '@element-plus/icons-vue';

const userStore = useUserStore();
const stats = ref({});

const loadData = async () => {
  const res = await request.get(`/video/creator/stats?user_id=${userStore.userInfo.id}`);
  if (res.data.code === 200) {
    stats.value = res.data.data;
  }
};
onMounted(() => loadData());
</script>

<style scoped>
.dashboard-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; }
.card { background: #fff; border: 1px solid #e5e5e5; border-radius: 6px; overflow: hidden; }
.card-header { padding: 16px 24px; font-weight: 500; font-size: 16px; border-bottom: 1px solid #f0f0f0; }
.video-snapshot { grid-column: span 1; }
.snapshot-content { padding: 20px; }
.thumb-box { margin-bottom: 15px; }
.thumb-box img { width: 100%; border-radius: 4px; aspect-ratio: 16/9; object-fit: cover; }
.v-title { margin-top: 10px; font-size: 14px; color: #0f0f0f; line-height: 1.4; }
.stat-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; color: #606060; font-size: 14px; }
.analytics-summary { grid-column: span 1; }
.summary-body { padding: 24px; }
.big-stat .label { font-size: 14px; color: #606060; }
.big-stat .value { font-size: 32px; font-weight: bold; color: #0f0f0f; margin-top: 5px; }
.stat-summary { margin-top: 10px; }
.stat-summary .label { font-weight: 500; font-size: 14px; }
.stat-summary .sub-label { font-size: 12px; color: #606060; margin-bottom: 10px; }
.stat-row-simple { display: flex; justify-content: space-between; font-size: 14px; padding: 5px 0; border-bottom: 1px solid #f9f9f9; }
.goto-analytics { margin-top: 20px; text-align: center; }
</style>