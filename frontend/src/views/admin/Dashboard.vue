<template>
  <div>
    <!-- 顶部卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6"><el-card><div class="stat-title">总用户数</div><div class="stat-num">{{ stats.total_users }}</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="stat-title">总视频数</div><div class="stat-num">{{ stats.total_videos }}</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="stat-title">待审核视频</div><div class="stat-num warning">{{ stats.pending_videos }}</div></el-card></el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card title="每日新增用户">
          <div ref="userChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card title="视频分类占比">
          <div ref="pieChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card title="热门视频 Top 10">
          <div ref="barChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import { getStats } from '../../api/admin';

const stats = ref({});
const userChartRef = ref(null);
const pieChartRef = ref(null);
const barChartRef = ref(null);

const initCharts = (data) => {
  // 1. 用户折线图
  const userChart = echarts.init(userChartRef.value);
  userChart.setOption({
    title: { text: '每日新增用户' },
    xAxis: { type: 'category', data: data.chart_users.dates },
    yAxis: { type: 'value' },
    series: [{ data: data.chart_users.counts, type: 'line', smooth: true }]
  });

  // 2. 分类饼图
  const pieChart = echarts.init(pieChartRef.value);
  pieChart.setOption({
    title: { text: '内容分布', left: 'center' },
    tooltip: { trigger: 'item' },
    series: [{ type: 'pie', radius: '50%', data: data.chart_category }]
  });

  // 3. Top10 柱状图
  const barChart = echarts.init(barChartRef.value);
  barChart.setOption({
    title: { text: '播放排行' },
    xAxis: { type: 'category', data: data.chart_top10.titles, axisLabel: { interval: 0, rotate: 30 } },
    yAxis: { type: 'value' },
    series: [{ data: data.chart_top10.views, type: 'bar' }]
  });
};

onMounted(async () => {
  const res = await getStats();
  if (res.data.code === 200) {
    stats.value = res.data.data;
    initCharts(res.data.data);
  }
});
</script>

<style scoped>
.stat-title { color: #999; font-size: 14px; }
.stat-num { font-size: 24px; font-weight: bold; margin-top: 10px; }
.warning { color: #E6A23C; }
</style>