<template>
  <div class="analytics-page">
    <h3>频道数据分析</h3>
    
    <!-- 1. 频道概览 (Top Stats) -->
    <div class="overview-cards">
      <el-card class="stat-card">
        <div class="stat-label">观看次数</div>
        <div class="stat-value">{{ stats.total_views }}</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-label">观看时长 (小时)</div>
        <div class="stat-value">{{ stats.total_watch_hours }}</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-label">订阅者</div>
        <div class="stat-value">{{ stats.total_fans }}</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-label">获赞次数</div>
        <div class="stat-value">{{ stats.total_likes }}</div>
      </el-card>
    </div>

    <!-- 2. 图表 (分类占比) -->
    <el-card class="chart-section">
      <div ref="chartRef" style="height: 300px; width: 100%;"></div>
    </el-card>

    <!-- 3. 视频详细分析列表 -->
    <div class="video-analytics-list">
      <h4>此期间发布的视频</h4>
      <el-table :data="stats.all_videos" style="width: 100%" @row-click="openVideoDetail" row-key="id" highlight-current-row>
        <el-table-column label="视频" min-width="300">
          <template #default="scope">
            <div class="video-cell">
              <div class="thumb-wrap">
                <img :src="scope.row.cover_url" class="cell-thumb" />
                <span class="duration">{{ formatTime(scope.row.duration) }}</span>
              </div>
              <div class="cell-info">
                <div class="cell-title">{{ scope.row.title }}</div>
                <div class="cell-date">{{ scope.row.upload_time }} 发布</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="观看次数" sortable />
        <el-table-column label="观看时长 (预估)">
           <template #default="scope">
             {{ ((scope.row.views * scope.row.duration) / 60).toFixed(1) }} 分钟
           </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
           <template #default="scope">
             <el-tag v-if="scope.row.status===1 && scope.row.visibility==='public'" type="success" size="small">公开</el-tag>
             <el-tag v-else-if="scope.row.visibility==='private'" type="info" size="small">私享</el-tag>
             <el-tag v-else type="warning" size="small">审核/下架</el-tag>
           </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 视频详细数据弹窗 -->
    <el-dialog v-model="detailVisible" title="视频分析" width="600px">
      <div v-if="selectedVideo" class="video-detail-modal">
        <div class="modal-header">
           <img :src="selectedVideo.cover_url" class="modal-cover">
           <div class="modal-info">
             <h3>{{ selectedVideo.title }}</h3>
             <p>发布于 {{ selectedVideo.upload_time }}</p>
           </div>
        </div>
        <el-divider />
        <div class="modal-stats">
           <div class="m-stat">
             <div class="label">播放量</div>
             <div class="val">{{ selectedVideo.views }}</div>
           </div>
           <div class="m-stat">
             <div class="label">总时长 (秒)</div>
             <div class="val">{{ selectedVideo.duration }}</div>
           </div>
           <div class="m-stat">
             <div class="label">预估观看时长 (分)</div>
             <div class="val">{{ ((selectedVideo.views * selectedVideo.duration) / 60).toFixed(1) }}</div>
           </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../../store/user';
import request from '../../api/request';
import * as echarts from 'echarts';

const userStore = useUserStore();
const chartRef = ref(null);
const stats = ref({ all_videos: [], total_watch_hours: 0, total_fans: 0, total_likes: 0, total_views: 0 });
const detailVisible = ref(false);
const selectedVideo = ref(null);

const loadData = async () => {
  const res = await request.get(`/video/creator/stats?user_id=${userStore.userInfo.id}`);
  if (res.data.code === 200) {
    stats.value = res.data.data;
    // 确保 DOM 渲染后再初始化图表
    setTimeout(() => {
        if (chartRef.value) initChart(res.data.data.chart_category);
    }, 100);
  }
};

const initChart = (data) => {
  const chart = echarts.init(chartRef.value);
  chart.setOption({
    title: { text: '内容受众分布', left: 'center' },
    tooltip: { trigger: 'item' },
    legend: { bottom: '0' },
    series: [{
        name: '分类', type: 'pie', radius: ['40%', '70%'],
        data: data, itemStyle: { borderRadius: 5 }
    }]
  });
};

const formatTime = (seconds) => {
  if (!seconds) return '00:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
};

const openVideoDetail = (row) => {
  selectedVideo.value = row;
  detailVisible.value = true;
};

onMounted(() => loadData());
</script>

<style scoped>
.analytics-page { padding: 0 20px; }
.overview-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }
.stat-card { text-align: center; }
.stat-label { font-size: 14px; color: #606060; }
.stat-value { font-size: 28px; font-weight: bold; color: #0f0f0f; margin-top: 5px; }

.chart-section { margin-bottom: 30px; }

.video-analytics-list { margin-top: 30px; }
.video-cell { display: flex; gap: 15px; align-items: center; }
.thumb-wrap { position: relative; width: 100px; height: 56px; flex-shrink: 0; }
.cell-thumb { width: 100%; height: 100%; object-fit: cover; border-radius: 4px; }
.duration { position: absolute; bottom: 2px; right: 2px; background: rgba(0,0,0,0.8); color: white; font-size: 10px; padding: 1px 3px; border-radius: 2px; }
.cell-info { display: flex; flex-direction: column; justify-content: center; }
.cell-title { font-weight: 500; color: #065fd4; cursor: pointer; font-size: 14px; }
.cell-date { font-size: 12px; color: #606060; }

/* 弹窗样式 */
.modal-header { display: flex; gap: 20px; align-items: flex-start; }
.modal-cover { width: 160px; aspect-ratio: 16/9; object-fit: cover; border-radius: 6px; }
.modal-info h3 { margin: 0 0 10px 0; font-size: 18px; }
.modal-info p { color: #606060; font-size: 14px; }
.modal-stats { display: flex; justify-content: space-around; margin-top: 20px; }
.m-stat { text-align: center; }
.m-stat .label { font-size: 12px; color: #909090; }
.m-stat .val { font-size: 24px; font-weight: bold; color: #0f0f0f; }
</style>