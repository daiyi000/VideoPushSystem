<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <div class="user-header">
        <el-avatar :size="80" :src="userInfo.avatar" class="u-avatar"></el-avatar>
        <div class="info">
          <h2>{{ userInfo.username }}</h2>
          <p class="email">{{ userInfo.email }}</p>
          <div style="margin-top: 10px;">
            <el-button type="primary" round size="small" @click="$router.push(`/channel/${userInfo.id}`)">前往我的频道</el-button>
          </div>
        </div>
      </div>

      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="profile-tabs">
        
        <el-tab-pane label="我的发布" name="videos">
          <el-table :data="myVideos" style="width: 100%" empty-text="暂无视频">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="views" label="播放" width="100" />
            <el-table-column prop="upload_time" label="发布时间" />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button type="danger" link @click="handleDelete(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="历史记录" name="history">
          <div v-if="myHistory.length > 0" class="video-grid">
            <div v-for="video in myHistory" :key="video.id" class="video-card" @click="$router.push(`/video/${video.id}`)">
              <div class="thumbnail-wrapper">
                <img :src="video.cover_url" class="thumbnail" />
              </div>
              <div class="video-info">
                <div class="video-title">{{ video.title }}</div>
                <div class="video-meta">观看于 {{ video.upload_time }}</div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无历史" />
        </el-tab-pane>

        <el-tab-pane label="我的收藏" name="favs">
          <div v-if="myFavs.length > 0" class="video-grid">
            <div v-for="video in myFavs" :key="video.id" class="video-card" @click="$router.push(`/video/${video.id}`)">
              <div class="thumbnail-wrapper">
                <img :src="video.cover_url" class="thumbnail" />
              </div>
              <div class="video-info">
                <div class="video-title">{{ video.title }}</div>
                <div class="video-meta">{{ video.views }}次播放</div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无收藏" />
        </el-tab-pane>

      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../store/user';
import { getMyVideos, getMyFavs, getMyHistory } from '../api/user';
import { deleteVideo } from '../api/video';
import { ElMessage, ElMessageBox } from 'element-plus';

const userStore = useUserStore();
const activeTab = ref('history'); // 默认看历史
const userInfo = ref({ ...userStore.userInfo });
const myVideos = ref([]);
const myFavs = ref([]);
const myHistory = ref([]);

const loadData = async (tabName) => {
  const uid = userStore.userInfo.id;
  const tab = tabName || activeTab.value;
  
  if (tab === 'videos') {
    const res = await getMyVideos(uid);
    myVideos.value = res.data.data;
  } else if (tab === 'favs') {
    const res = await getMyFavs(uid);
    myFavs.value = res.data.data;
  } else if (tab === 'history') {
    const res = await getMyHistory(uid);
    myHistory.value = res.data.data;
  }
};

const handleTabClick = (ctx) => loadData(ctx.props.name);

const handleDelete = (id) => {
  ElMessageBox.confirm('删除视频？').then(async () => {
    await deleteVideo(id);
    ElMessage.success('已删除');
    loadData('videos');
  });
};

onMounted(() => loadData());
</script>

<style scoped>
.profile-container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
.profile-card { border-radius: 16px; border: none; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }

.user-header { display: flex; align-items: center; margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #f0f0f0; }
.u-avatar { border: 1px solid #eee; }
.info { margin-left: 24px; }
.info h2 { margin: 0 0 5px 0; color: #0f0f0f; }
.email { color: #606060; margin: 0; }

.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
.video-card { cursor: pointer; transition: transform 0.2s; }
.video-card:hover { transform: translateY(-3px); }
.thumbnail-wrapper { width: 100%; aspect-ratio: 16/9; background: #eee; border-radius: 12px; overflow: hidden; margin-bottom: 8px; }
.thumbnail { width: 100%; height: 100%; object-fit: cover; }
.video-title { font-size: 14px; font-weight: 600; color: #0f0f0f; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.video-meta { font-size: 12px; color: #606060; }
</style>