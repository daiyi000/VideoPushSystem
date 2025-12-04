<template>
  <div class="channel-container">
    <div class="channel-layout">
      
      <!-- 1. 频道头部 -->
      <div class="channel-header">
        <!-- 动态横幅 -->
        <div class="channel-banner" :style="bannerStyle"></div>
        
        <div class="header-content">
          <div class="avatar-section">
            <el-avatar :size="128" :src="author.avatar" class="channel-avatar" />
          </div>
          
          <div class="info-section">
            <h1 class="channel-name">{{ author.username }}</h1>
            <div class="channel-meta">
              <span class="meta-item">{{ author.email || 'VideoHub 用户' }}</span>
              <span class="meta-item">{{ stats.fans }} 位订阅者</span>
              <span class="meta-item">{{ videoList.length }} 个视频</span>
            </div>
            <div class="channel-desc">{{ author.description || '这个人很懒，什么都没写' }}</div>
            
            <div class="subscribe-btn-wrapper">
              <button 
                v-if="!isOwner"
                class="yt-sub-btn" 
                :class="{ subscribed: stats.is_following }"
                @click="handleSubscribe"
              >
                {{ stats.is_following ? '已订阅' : '订阅' }}
              </button>
              
              <div v-else class="owner-actions">
                <el-button type="primary" round @click="openEditDialog">自定义频道</el-button>
                <el-button round @click="manageDialogVisible = true">管理视频</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 内容导航 -->
      <div class="channel-nav">
        <div class="nav-tabs">
          <div class="nav-tab" :class="{ active: activeTab === 'videos' }" @click="activeTab = 'videos'">视频</div>
          <div class="nav-tab" :class="{ active: activeTab === 'playlists' }" @click="activeTab = 'playlists'">播放列表</div>
        </div>
        
        <div class="nav-filters" v-if="activeTab === 'videos'">
          <el-select v-model="sortBy" placeholder="排序" size="small" style="width: 110px" @change="loadData">
            <el-option label="最新发布" value="new" />
            <el-option label="最受欢迎" value="hot" />
            <el-option label="最早发布" value="old" />
          </el-select>
          <div class="channel-search">
            <el-icon class="search-icon"><Search /></el-icon>
            <input v-model="searchQuery" placeholder="搜索" @keyup.enter="loadData" />
          </div>
        </div>
      </div>

      <el-divider style="margin: 0;" />

      <!-- 3. Tab 内容区 -->
      <div class="content-section">
        
        <!-- A. 视频列表 -->
        <div v-if="activeTab === 'videos'">
          <div v-if="videoList.length > 0" class="video-grid">
            <div v-for="video in videoList" :key="video.id" class="video-card" @click="$router.push(`/video/${video.id}`)">
              <div class="thumbnail-wrapper">
                <img :src="video.cover_url" class="thumbnail" />
                <span class="duration">HD</span>
              </div>
              <div class="video-info">
                <h3 class="video-title" :title="video.title">{{ video.title }}</h3>
                <div class="video-meta">
                  {{ video.views }}次观看 • {{ video.upload_time.split(' ')[0] }}
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="该作者还没有相关视频" />
        </div>

        <!-- B. 播放列表 (卡片样式升级) -->
        <div v-if="activeTab === 'playlists'">
          <!-- 创建按钮 (仅自己可见) -->
          <div v-if="isOwner" style="margin-bottom: 20px;">
            <el-button type="primary" plain @click="openPlaylistDialog">+ 新建播放列表</el-button>
          </div>

          <div v-if="playlists.length > 0" class="playlist-grid">
            <!-- 升级后的播放列表卡片 -->
            <div v-for="pl in playlists" :key="pl.id" class="playlist-card-new" @click="handleViewPlaylist(pl)">
              <!-- 封面区域 -->
              <div class="pl-thumb-container">
                <!-- 堆叠效果层 -->
                <div class="pl-stack-layer"></div>
                <!-- 主图 -->
                <div class="pl-thumb-wrapper">
                  <img :src="pl.cover_url" class="pl-img">
                  <!-- 底部黑色半透明条 -->
                  <div class="pl-count-bar">
                    <el-icon><List /></el-icon>
                    <span>{{ pl.count }}个视频</span>
                  </div>
                  <!-- 悬停时的播放遮罩 -->
                  <div class="pl-hover-overlay">
                    <el-icon size="40"><VideoPlay /></el-icon>
                    <span>全部播放</span>
                  </div>
                </div>
              </div>
              
              <!-- 信息区域 -->
              <div class="pl-info-new">
                <div class="pl-title-new">{{ pl.title }}</div>
                <div class="pl-link-text">查看完整播放列表</div>
                <div class="pl-action-row" v-if="isOwner">
                   <el-button type="danger" link size="small" @click.stop="handleDeletePlaylist(pl.id)">删除</el-button>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无播放列表" />
        </div>

      </div>
    </div>

    <!-- 弹窗 1: 编辑频道 -->
    <el-dialog v-model="editDialogVisible" title="自定义频道" width="500px">
      <el-form label-width="80px">
        <el-form-item label="横幅图片">
          <div class="banner-uploader" @click="triggerBannerInput">
            <img v-if="editForm.banner" :src="editForm.banner" class="banner-preview" />
            <div class="upload-mask">点击更换横幅</div>
          </div>
          <input type="file" ref="bannerInput" style="display: none" accept="image/*" @change="handleBannerUpload" />
        </el-form-item>
        
        <el-form-item label="头像">
          <div class="avatar-uploader" @click="triggerFileInput">
            <img v-if="editForm.avatar" :src="editForm.avatar" class="avatar-preview" />
            <div class="upload-mask">修改</div>
          </div>
          <input type="file" ref="fileInput" style="display: none" accept="image/*" @change="handleAvatarUpload" />
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>

    <!-- 弹窗 2: 管理所有视频 -->
    <el-dialog v-model="manageDialogVisible" title="视频管理" width="800px">
      <el-table :data="videoList" height="400">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="views" label="播放" width="80" />
        <el-table-column prop="upload_time" label="发布时间" width="180" />
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="danger" size="small" @click="handleDeleteVideo(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 弹窗 3: 新建播放列表 -->
    <el-dialog v-model="playlistDialogVisible" title="新建播放列表" width="400px">
      <el-input v-model="newPlaylistName" placeholder="输入列表名称" />
      <template #footer>
        <el-button type="primary" @click="handleCreatePlaylist">创建</el-button>
      </template>
    </el-dialog>

    <!-- 弹窗 4: 查看播放列表详情 (模仿页面布局) -->
    <el-dialog 
      v-model="viewPlaylistDialogVisible" 
      width="1000px" 
      :show-close="true"
      class="yt-playlist-dialog"
      align-center
    >
      <div class="yt-pl-layout">
        <!-- 左侧：播放列表信息卡片 -->
        <div class="yt-pl-sidebar" :style="{ backgroundImage: `url(${currentPlaylist?.cover_url})` }">
           <!-- 背景模糊层 -->
           <div class="yt-pl-bg-blur"></div>
           <!-- 内容层 -->
           <div class="yt-pl-content">
              <div class="yt-pl-cover-box">
                <img :src="currentPlaylist?.cover_url" class="yt-pl-cover-img">
              </div>
              <h2 class="yt-pl-title">{{ currentPlaylist?.title }}</h2>
              <div class="yt-pl-owner">{{ author.username }}</div>
              <div class="yt-pl-meta">
                <span>{{ currentPlaylist?.count }}个视频</span> • <span>{{ currentPlaylist?.created_at }}更新</span>
              </div>
              
              <!-- 操作按钮组 -->
              <div class="yt-pl-actions">
                 <el-button type="primary" round class="play-all-btn" v-if="currentPlaylistVideos.length > 0" @click="goToVideo(currentPlaylistVideos[0].id)">
                    <el-icon style="margin-right:5px"><VideoPlay /></el-icon> 播放全部
                 </el-button>
                 <el-button type="primary" round class="play-all-btn" v-if="isOwner" @click="addToPlVisible = true">
                    <el-icon style="margin-right:5px"><Plus /></el-icon> 添加视频
                 </el-button>
              </div>
           </div>
        </div>

        <!-- 右侧：视频列表 -->
        <div class="yt-pl-list-container">
          <div v-if="currentPlaylistVideos.length > 0">
            <div 
              v-for="(v, index) in currentPlaylistVideos" 
              :key="v.id" 
              class="yt-pl-item" 
              @click="goToVideo(v.id)"
            >
              <div class="yt-pl-index">{{ index + 1 }}</div>
              <div class="yt-pl-thumb-box">
                <img :src="v.cover_url" class="yt-pl-thumb">
              </div>
              <div class="yt-pl-info">
                <div class="yt-pl-v-title">{{ v.title }}</div>
                <div class="yt-pl-v-meta">
                  <span>{{ author.username }}</span> • <span>{{ v.views }}次播放</span>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="该播放列表为空" />
        </div>
      </div>
    </el-dialog>

    <!-- 弹窗 5: 选择视频加入列表 (仅主人可见) -->
    <el-dialog v-model="addToPlVisible" title="选择视频加入列表" width="500px">
      <div class="mini-video-list">
        <div v-for="v in videoList" :key="v.id" class="mini-video-item" @click="addVideoToPl(v.id)">
          <img :src="v.cover_url" />
          <span>{{ v.title }}</span>
          <el-icon><Plus /></el-icon>
        </div>
      </div>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
import { getChannelInfo, toggleFollow, updateProfile, uploadAvatar, uploadBanner } from '../api/user';
import { createPlaylist, deletePlaylist, addVideoToPlaylist, getPlaylistVideos } from '../api/playlist'; 
import { deleteVideo } from '../api/video';
import { Search, Plus, List, VideoPlay } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const authorId = route.params.id;
const author = ref({});
const stats = ref({ fans: 0, is_following: false });
const videoList = ref([]);
const playlists = ref([]);

const activeTab = ref('videos');
const sortBy = ref('new');
const searchQuery = ref('');

// 弹窗状态
const editDialogVisible = ref(false);
const manageDialogVisible = ref(false);
const playlistDialogVisible = ref(false);
const viewPlaylistDialogVisible = ref(false); // 查看详情弹窗
const addToPlVisible = ref(false); // 添加视频弹窗

const editForm = ref({ username: '', avatar: '', banner: '', description: '' });
const fileInput = ref(null);
const bannerInput = ref(null);
const newPlaylistName = ref('');

// 当前选中的播放列表
const currentPlaylist = ref(null);
const currentPlaylistVideos = ref([]);

const isOwner = computed(() => userStore.token && String(userStore.userInfo.id) === String(authorId));

const bannerStyle = computed(() => ({
  backgroundImage: author.value.banner ? `url(${author.value.banner})` : 'linear-gradient(90deg, #cc2b5e 0%, #753a88 100%)',
  backgroundSize: 'cover',
  backgroundPosition: 'center'
}));

const loadData = async () => {
  try {
    const res = await getChannelInfo({
      author_id: authorId,
      visitor_id: userStore.token ? userStore.userInfo.id : null,
      sort_by: sortBy.value,
      q: searchQuery.value
    });
    if (res.data.code === 200) {
      const d = res.data.data;
      author.value = d.author;
      stats.value = d.stats;
      videoList.value = d.videos;
      playlists.value = d.playlists;
    }
  } catch (e) { console.error(e); }
};

const handleSubscribe = async () => {
  if (!userStore.token) return ElMessage.warning('请先登录');
  try {
    const res = await toggleFollow({ follower_id: userStore.userInfo.id, followed_id: authorId });
    if (res.data.code === 200) {
      stats.value.is_following = res.data.is_following;
      stats.value.fans = res.data.fans_count;
      ElMessage.success(res.data.is_following ? '订阅成功' : '已取消订阅');
    }
  } catch (e) { ElMessage.error('操作失败'); }
};

// --- 播放列表逻辑 ---
const openPlaylistDialog = () => { newPlaylistName.value = ''; playlistDialogVisible.value = true; };
const handleCreatePlaylist = async () => {
  if (!newPlaylistName.value) return;
  const res = await createPlaylist({ title: newPlaylistName.value, user_id: userStore.userInfo.id });
  if (res.data.code === 200) {
    ElMessage.success('创建成功');
    loadData();
    playlistDialogVisible.value = false;
  }
};
const handleDeletePlaylist = (id) => {
  ElMessageBox.confirm('确定删除？', '提示').then(async () => {
    await deletePlaylist(id);
    loadData();
  });
};

// 查看播放列表详情 (API请求)
const handleViewPlaylist = async (pl) => {
  currentPlaylist.value = pl;
  try {
    const res = await getPlaylistVideos(pl.id);
    if (res.data.code === 200) {
      currentPlaylistVideos.value = res.data.data;
      viewPlaylistDialogVisible.value = true;
    }
  } catch (e) {
    ElMessage.error('获取列表失败');
  }
};

const goToVideo = (vid) => {
  router.push(`/video/${vid}`);
};

// 添加视频到列表
const addVideoToPl = async (vid) => {
  const res = await addVideoToPlaylist({ playlist_id: currentPlaylist.value.id, video_id: vid });
  if (res.data.code === 200) {
    ElMessage.success(res.data.msg);
    addToPlVisible.value = false;
    // 刷新当前弹窗里的视频列表
    const refreshRes = await getPlaylistVideos(currentPlaylist.value.id);
    currentPlaylistVideos.value = refreshRes.data.data;
    // 刷新外面的计数
    loadData();
  }
};

// --- 编辑与管理 ---
const openEditDialog = () => { editForm.value = { ...author.value }; editDialogVisible.value = true; };
const triggerFileInput = () => fileInput.value.click();
const triggerBannerInput = () => bannerInput.value.click();
const handleAvatarUpload = async (e) => { const file = e.target.files[0]; if (!file) return; const formData = new FormData(); formData.append('file', file); const res = await uploadAvatar(formData); if (res.data.code === 200) editForm.value.avatar = res.data.url; };
const handleBannerUpload = async (e) => { const file = e.target.files[0]; if (!file) return; const formData = new FormData(); formData.append('file', file); const res = await uploadBanner(formData); if (res.data.code === 200) editForm.value.banner = res.data.url; };
const saveProfile = async () => { const res = await updateProfile({ user_id: userStore.userInfo.id, ...editForm.value }); if (res.data.code === 200) { ElMessage.success('保存成功'); author.value = res.data.data; userStore.setLoginState(userStore.token, res.data.data); editDialogVisible.value = false; } };
const handleDeleteVideo = (id) => { ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' }).then(async () => { await deleteVideo(id); loadData(); ElMessage.success('删除成功'); }); };

watch(() => route.params.id, () => loadData());
onMounted(() => loadData());
</script>

<style scoped>
.channel-container { background: #f9f9f9; min-height: 100vh; padding-bottom: 40px; }
.channel-layout { max-width: 1200px; margin: 0 auto; background: #fff; min-height: 100vh; }

.channel-banner { height: 180px; background-color: #eee; }
.header-content { padding: 0 50px; display: flex; align-items: flex-start; margin-top: -30px; margin-bottom: 20px; }
.avatar-section { margin-right: 24px; border-radius: 50%; padding: 4px; background: #fff; }
.info-section { padding-top: 40px; flex: 1; }
.channel-name { font-size: 28px; font-weight: bold; margin: 0 0 5px 0; color: #0f0f0f; }
.channel-meta { color: #606060; font-size: 14px; margin-bottom: 10px; display: flex; gap: 10px; }
.channel-desc { color: #606060; font-size: 14px; margin-bottom: 15px; max-width: 600px; }

.yt-sub-btn { background: #0f0f0f; color: #fff; border: none; padding: 0 16px; height: 36px; border-radius: 18px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; }
.yt-sub-btn:hover { background: #272727; }
.yt-sub-btn.subscribed { background: #f2f2f2; color: #0f0f0f; }
.owner-actions { display: flex; gap: 10px; }

.channel-nav { padding: 0 50px; display: flex; justify-content: space-between; align-items: center; height: 48px; }
.nav-tabs { display: flex; gap: 30px; height: 100%; }
.nav-tab { font-size: 15px; font-weight: 500; color: #606060; cursor: pointer; text-transform: uppercase; display: flex; align-items: center; border-bottom: 3px solid transparent; }
.nav-tab.active { color: #0f0f0f; border-bottom-color: #0f0f0f; }
.nav-filters { display: flex; align-items: center; gap: 10px; }
.channel-search { display: flex; align-items: center; gap: 5px; font-size: 14px; border-bottom: 1px solid #ccc; padding: 0 5px; }
.channel-search input { border: none; outline: none; width: 100px; font-size: 14px; background: transparent; }

.content-section { padding: 30px 50px; }
.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 20px; row-gap: 30px; }
.video-card { cursor: pointer; }
.thumbnail-wrapper { width: 100%; aspect-ratio: 16/9; background: #eee; border-radius: 8px; overflow: hidden; position: relative; margin-bottom: 10px; }
.thumbnail { width: 100%; height: 100%; object-fit: cover; }
.duration { position: absolute; bottom: 5px; right: 5px; background: rgba(0,0,0,0.8); color: white; padding: 2px 4px; border-radius: 4px; font-size: 12px; }
.video-title { font-size: 14px; font-weight: 600; line-height: 1.4; color: #0f0f0f; margin: 0 0 4px 0; }
.video-meta { font-size: 12px; color: #606060; }

/* --- 升级后的播放列表卡片样式 --- */
.playlist-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 20px; }
.playlist-card-new { cursor: pointer; }

.pl-thumb-container {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  margin-bottom: 10px;
}

/* 堆叠效果层 (顶部灰色条) */
.pl-stack-layer {
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  height: 4px;
  background: #d0d0d0;
  border-radius: 4px 4px 0 0;
  z-index: 0;
}
/* 主封面容器 */
.pl-thumb-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
  background: #eee;
  z-index: 1;
}
.pl-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.2s;
}
/* 底部数量条 */
.pl-count-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 28px;
  background: rgba(0,0,0,0.7);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  backdrop-filter: blur(2px);
}
/* 悬停播放遮罩 */
.pl-hover-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.2s;
}
.playlist-card-new:hover .pl-hover-overlay { opacity: 1; }

.pl-info-new .pl-title-new { font-weight: 600; font-size: 14px; color: #0f0f0f; margin-bottom: 4px; }
.pl-link-text { font-size: 12px; color: #606060; font-weight: 600; margin-bottom: 4px; }
.pl-action-row { margin-top: 2px; }

/* --- 播放列表详情弹窗 (YouTube Layout) --- */
/* 左侧栏 */
.yt-pl-layout { display: flex; height: 500px; overflow: hidden; }
.yt-pl-sidebar {
  width: 360px;
  flex-shrink: 0;
  padding: 24px;
  position: relative;
  overflow: hidden;
  background-size: cover;
  background-position: center;
  display: flex;
  flex-direction: column;
  color: white;
}
/* 背景毛玻璃 */
.yt-pl-bg-blur {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  backdrop-filter: blur(40px) brightness(0.6);
  background: rgba(0,0,0,0.5);
  z-index: 0;
}
.yt-pl-content { position: relative; z-index: 1; display: flex; flex-direction: column; height: 100%; }
.yt-pl-cover-box {
  width: 100%;
  aspect-ratio: 16/9;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  margin-bottom: 20px;
}
.yt-pl-cover-img { width: 100%; height: 100%; object-fit: cover; }
.yt-pl-title { font-size: 24px; font-weight: bold; margin: 0 0 10px 0; }
.yt-pl-owner { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
.yt-pl-meta { font-size: 12px; margin-bottom: 20px; opacity: 0.9; }
.yt-pl-actions { margin-top: auto; display: flex; flex-direction: column; gap: 10px; }
.play-all-btn { width: 100%; background: white; color: black; border: none; font-weight: 600; }
.play-all-btn:hover { background: #eee; color: black; }

/* 右侧列表 */
.yt-pl-list-container { flex: 1; background: #fff; overflow-y: auto; padding: 10px 0; }
.yt-pl-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  cursor: pointer;
  transition: background 0.1s;
}
.yt-pl-item:hover { background: #f2f2f2; }
.yt-pl-index { width: 30px; color: #606060; font-size: 14px; }
.yt-pl-thumb-box { width: 120px; height: 68px; border-radius: 8px; overflow: hidden; margin-right: 15px; flex-shrink: 0; }
.yt-pl-thumb { width: 100%; height: 100%; object-fit: cover; }
.yt-pl-info { flex: 1; min-width: 0; }
.yt-pl-v-title { font-size: 14px; font-weight: 600; color: #0f0f0f; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.yt-pl-v-meta { font-size: 12px; color: #606060; }

/* 弹窗样式调整 */
:deep(.yt-playlist-dialog .el-dialog__body) { padding: 0; }
:deep(.yt-playlist-dialog .el-dialog__header) { display: none; } /* 隐藏原生标题 */

/* 弹窗样式 */
.avatar-uploader, .banner-uploader { border: 1px dashed #d9d9d9; cursor: pointer; position: relative; overflow: hidden; display: flex; justify-content: center; align-items: center; background: #fafafa; }
.avatar-uploader { width: 100px; height: 100px; border-radius: 50%; }
.banner-uploader { width: 100%; height: 100px; border-radius: 4px; }
.avatar-preview, .banner-preview { width: 100%; height: 100%; object-fit: cover; }
.upload-mask { position: absolute; bottom: 0; width: 100%; background: rgba(0,0,0,0.5); color: white; font-size: 12px; text-align: center; line-height: 24px; }

.mini-video-list { max-height: 300px; overflow-y: auto; }
.mini-video-item { display: flex; align-items: center; gap: 10px; padding: 8px; cursor: pointer; border-bottom: 1px solid #eee; }
.mini-video-item:hover { background: #f5f7fa; }
.mini-video-item img { width: 60px; height: 34px; object-fit: cover; border-radius: 2px; }
.mini-video-item span { flex: 1; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>