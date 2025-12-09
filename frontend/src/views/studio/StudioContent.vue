<template>
  <div class="content-page">
    <h3>频道内容</h3>
    
    <el-tabs v-model="activeTab">
      <el-tab-pane label="视频" name="videos">
        <el-table :data="videoList" style="width: 100%" :header-cell-style="{background:'#f9f9f9'}">
          <el-table-column label="视频" min-width="300">
            <template #default="scope">
              <div class="video-cell">
                <img :src="scope.row.cover_url" class="cell-thumb" />
                <div class="cell-info">
                  <div class="cell-title">{{ scope.row.title }}</div>
                  <div class="cell-desc">{{ scope.row.description?.substring(0, 30) }}...</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="可见性" width="100">
            <template #default="scope">
               <div style="display:flex;align-items:center;gap:5px">
                 <el-icon color="#67C23A"><View /></el-icon> 公开
               </div>
            </template>
          </el-table-column>
          <el-table-column prop="upload_time" label="日期" width="180" sortable />
          <el-table-column prop="views" label="观看次数" width="120" sortable />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button type="primary" link icon="Edit" @click="$router.push(`/video/${scope.row.id}`)">查看</el-button>
              <el-button type="danger" link icon="Delete" @click="handleDelete(scope.row.id)"></el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../../store/user';
import { getMyVideos } from '../../api/user';
import { deleteVideo } from '../../api/video';
import { View, Edit, Delete } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const userStore = useUserStore();
const activeTab = ref('videos');
const videoList = ref([]);

const loadData = async () => {
  const res = await getMyVideos(userStore.userInfo.id);
  videoList.value = res.data.data;
};

const handleDelete = (id) => {
  ElMessageBox.confirm('永久删除此视频？此操作无法撤销。', '删除视频', { type: 'warning' })
    .then(async () => {
      await deleteVideo(id);
      ElMessage.success('已删除');
      loadData();
    });
};

onMounted(() => loadData());
</script>

<style scoped>
.content-page { background: #fff; padding: 0; min-height: 100%; }
.video-cell { display: flex; gap: 15px; align-items: flex-start; }
.cell-thumb { width: 120px; height: 68px; object-fit: cover; border-radius: 4px; flex-shrink: 0; }
.cell-info { display: flex; flex-direction: column; justify-content: center; }
.cell-title { font-size: 14px; font-weight: 500; color: #0f0f0f; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;}
.cell-desc { font-size: 12px; color: #606060; }
</style>