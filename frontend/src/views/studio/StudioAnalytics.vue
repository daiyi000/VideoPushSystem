<template>
  <div>
    <h3>频道数据分析</h3>
    <div style="margin-top: 20px;">
       <el-card>
         <div ref="chartRef" style="height: 300px; width: 100%;"></div>
       </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../../store/user';
import request from '../../api/request';
import * as echarts from 'echarts';

const userStore = useUserStore();
const chartRef = ref(null);

onMounted(async () => {
  const res = await request.get(`/video/creator/stats?user_id=${userStore.userInfo.id}`);
  if (res.data.code === 200) {
    const data = res.data.data.chart_category || [];
    
    const chart = echarts.init(chartRef.value);
    chart.setOption({
      title: { text: '您的内容受众分布 (按分类)' },
      tooltip: { trigger: 'item' },
      series: [
        {
          name: '分类',
          type: 'pie',
          radius: ['40%', '70%'],
          data: data,
          itemStyle: { borderRadius: 5 }
        }
      ]
    });
  }
});
</script>