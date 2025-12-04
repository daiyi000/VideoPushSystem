<template>
  <div class="audit-container">
    <el-page-header @back="$router.go(-1)" content="视频审核详情" style="margin-bottom: 20px;" />

    <div v-if="video" class="audit-layout">
      <!-- 左侧：视频播放区 -->
      <div class="video-section">
        <div class="player-wrapper">
          <video :src="video.url" controls autoplay class="audit-player"></video>
        </div>
      </div>

      <!-- 右侧：审核控制台 -->
      <div class="control-section">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-tag :type="statusType(video.status)">{{ statusText(video.status) }}</el-tag>
            </div>
          </template>
          
          <div class="info-item">
            <span class="label">封面：</span>
            <img :src="video.cover_url" class="cover-preview" />
          </div>
          <div class="info-item">
            <span class="label">标题：</span>
            <span class="value title">{{ video.title }}</span>
          </div>
          <div class="info-item">
            <span class="label">作者：</span>
            <span class="value">{{ video.uploader_name }} (ID: {{ video.uploader_id }})</span>
          </div>
          <div class="info-item">
            <span class="label">分类：</span>
            <el-tag size="small">{{ video.category }}</el-tag>
          </div>
          <div class="info-item">
            <span class="label">简介：</span>
            <p class="value desc">{{ video.description || '无简介' }}</p>
          </div>
          <div class="info-item">
            <span class="label">标签：</span>
            <span class="value">{{ video.tags || '无标签' }}</span>
          </div>
          <div class="info-item">
            <span class="label">时间：</span>
            <span class="value">{{ video.upload_time }}</span>
          </div>
        </el-card>

        <el-card class="action-card">
          <template #header>
            <div class="card-header">审核操作</div>
          </template>
          
          <div class="action-buttons">
            <el-button type="success" size="large" icon="Check" @click="handleAudit(1)">通过发布</el-button>
            <el-button type="danger" size="large" icon="Close" @click="handleAudit(2)">拒绝/下架</el-button>
          </div>
          <div style="margin-top: 15px; text-align: center;">
            <el-button type="info" link @click="$router.go(-1)">暂不处理，返回列表</el-button>
          </div>
        </el-card>
      </div>
    </div>
    
    <el-skeleton v-else :rows="10" animated />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getVideoDetail } from '../../api/video'; // 复用获取详情接口
import { auditVideo } from '../../api/admin';     // 引入审核接口
import { ElMessage, ElMessageBox } from 'element-plus';
import { Check, Close } from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const video = ref(null);

const videoId = route.params.id;

// 加载视频详情
const loadData = async () => {
  try {
    const res = await getVideoDetail(videoId);
    if (res.data.code === 200) {
      video.value = res.data.data;
    }
  } catch (error) {
    console.error(error);
    ElMessage.error('无法加载视频信息，可能已被删除');
  }
};

// 提交审核结果
const handleAudit = (status) => {
  const actionText = status === 1 ? '通过' : '拒绝/下架';
  
  ElMessageBox.confirm(`确定要${actionText}该视频吗？`, '审核确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: status === 1 ? 'success' : 'warning'
  }).then(async () => {
    try {
      await auditVideo({ id: videoId, status: status });
      ElMessage.success('操作成功');
      router.push('/admin/videos'); // 审核完跳回列表
    } catch (e) {
      ElMessage.error('操作失败');
    }
  });
};

// 状态辅助函数
const statusType = (s) => {
  if (s === 0) return 'warning';
  if (s === 1) return 'success';
  return 'danger';
};
const statusText = (s) => {
  if (s === 0) return '待审核';
  if (s === 1) return '已发布';
  return '已下架';
};

onMounted(() => loadData());
</script>

<style scoped>
.audit-container { padding: 20px; }
.audit-layout { display: flex; gap: 20px; height: calc(100vh - 120px); }

/* 左侧播放器 */
.video-section { flex: 2; background: black; border-radius: 8px; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.player-wrapper { width: 100%; height: 100%; }
.audit-player { width: 100%; height: 100%; object-fit: contain; }

/* 右侧信息栏 */
.control-section { flex: 1; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
.info-card, .action-card { border-radius: 8px; }
.card-header { font-weight: bold; display: flex; justify-content: space-between; align-items: center; }

.info-item { margin-bottom: 12px; display: flex; font-size: 14px; }
.label { width: 60px; color: #909399; flex-shrink: 0; }
.value { color: #303133; flex: 1; word-break: break-all; }
.value.title { font-weight: bold; font-size: 16px; }
.value.desc { color: #606266; line-height: 1.5; margin: 0; white-space: pre-wrap; }
.cover-preview { width: 120px; height: 68px; object-fit: cover; border-radius: 4px; border: 1px solid #eee; }

.action-buttons { display: flex; flex-direction: column; gap: 15px; padding: 10px 0; }
.action-buttons .el-button { margin-left: 0; height: 50px; font-size: 16px; }
</style>