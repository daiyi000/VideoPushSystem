<template>
  <div class="channel-container">
    <div class="channel-layout">
      
      <!-- 1. 频道头部 -->
      <div class="channel-header">
        <!-- 动态横幅 (触发裁剪) -->
        <div 
          class="channel-banner" 
          :style="bannerStyle" 
          @click="isOwner ? triggerBannerSelect() : null"
          :class="{ 'is-owner': isOwner }"
        >
          <div class="edit-overlay" v-if="isOwner">
            <el-icon><Camera /></el-icon><span>更换横幅</span>
          </div>
          <!-- 隐藏的原生 input -->
          <input type="file" ref="bannerInput" style="display: none" accept="image/*" @change="onFileSelect($event, 'banner')" />
        </div>
        
        <div class="header-content">
          <!-- 头像 (触发裁剪) -->
          <div 
            class="avatar-section" 
            @click="isOwner ? triggerAvatarSelect() : null"
            :class="{ 'is-owner': isOwner }"
          >
            <el-avatar :size="128" :src="author.avatar" class="channel-avatar" />
            <div class="avatar-edit-mask" v-if="isOwner"><el-icon><Camera /></el-icon></div>
            <input type="file" ref="avatarInput" style="display: none" accept="image/*" @change="onFileSelect($event, 'avatar')" />
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
              <button v-if="!isOwner" class="yt-sub-btn" :class="{ subscribed: stats.is_following }" @click="handleSubscribe">
                {{ stats.is_following ? '已订阅' : '订阅' }}
              </button>
              <div v-else class="owner-actions">
                <el-button round class="action-btn" @click="openEditDialog">自定义频道</el-button>
                <el-button round class="action-btn" @click="manageDialogVisible = true">管理视频</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 内容导航 -->
      <div class="channel-nav">
        <div class="nav-tabs">
          <div class="nav-tab" :class="{ active: activeTab === 'videos' }" @click="activeTab = 'videos'">视频</div>
          <div class="nav-tab" :class="{ active: activeTab === 'playlists' }" @click="activeTab = 'playlists'">播放列表</div>
        </div>
        <div class="nav-filters" v-if="activeTab === 'videos'">
          <el-select v-model="sortBy" placeholder="排序" size="small" style="width: 110px" @change="loadData">
            <el-option label="最新发布" value="new" /><el-option label="最受欢迎" value="hot" /><el-option label="最早发布" value="old" />
          </el-select>
          <div class="channel-search">
            <el-icon class="search-icon"><Search /></el-icon>
            <input v-model="searchQuery" placeholder="搜索" @keyup.enter="loadData" />
          </div>
        </div>
      </div>
      <el-divider style="margin: 0; border-color: #e5e5e5;" />

      <!-- Tab 内容区 -->
      <div class="content-section">
        <div v-if="activeTab === 'videos'">
          <div v-if="videoList.length > 0" class="video-grid">
            <div v-for="video in videoList" :key="video.id" class="video-card" @click="goToVideo(video.id)">
              <div class="thumbnail-wrapper"><img :src="video.cover_url" class="thumbnail" /><span class="duration">HD</span></div>
              <div class="video-info"><h3 class="video-title" :title="video.title">{{ video.title }}</h3><div class="video-meta">{{ video.views }}次观看 • {{ video.upload_time.split(' ')[0] }}</div></div>
            </div>
          </div>
          <el-empty v-else description="该作者还没有相关视频" />
        </div>
        <div v-if="activeTab === 'playlists'">
          <div v-if="isOwner" style="margin-bottom: 20px;"><el-button type="primary" plain @click="openPlaylistDialog">+ 新建播放列表</el-button></div>
          <div v-if="playlists.length > 0" class="playlist-grid">
            <div v-for="pl in playlists" :key="pl.id" class="playlist-card-new" @click="handleViewPlaylist(pl)">
              <div class="pl-thumb-container">
                <div class="pl-stack-layer"></div>
                <div class="pl-thumb-wrapper">
                  <img :src="pl.cover_url" class="pl-img">
                  <div class="pl-count-bar"><el-icon><List /></el-icon><span>{{ pl.count }}个视频</span></div>
                  <div class="pl-hover-overlay"><el-icon size="40"><VideoPlay /></el-icon><span>查看列表</span></div>
                </div>
              </div>
              <div class="pl-info-new"><div class="pl-title-new">{{ pl.title }}</div><div class="pl-link-text">查看完整播放列表</div></div>
            </div>
          </div>
          <el-empty v-else description="暂无播放列表" />
        </div>
      </div>
    </div>

    <!-- 弹窗 1: 编辑资料 (不含头像横幅，只改文字) -->
    <el-dialog v-model="editDialogVisible" title="自定义频道" width="500px" style="border-radius: 12px;">
      <el-form label-width="60px">
        <el-form-item label="名称"><el-input v-model="editForm.username" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="editForm.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>

    <!-- 引入裁剪组件 -->
    <ImageCropper ref="avatarCropperRef" title="裁剪头像" :aspect-ratio="1" @upload="doUploadAvatar" />
    <ImageCropper ref="bannerCropperRef" title="裁剪横幅" :aspect-ratio="4" @upload="doUploadBanner" />

    <!-- 其他弹窗 (管理视频/播放列表等，保持不变) -->
    <el-dialog v-model="manageDialogVisible" title="视频管理" width="800px" style="border-radius: 12px;">
      <el-table :data="videoList" height="400">
        <el-table-column prop="title" label="标题" />
        <el-table-column label="操作" width="100"><template #default="scope"><el-button type="danger" size="small" @click="handleDeleteVideo(scope.row.id)">删除</el-button></template></el-table-column>
      </el-table>
    </el-dialog>
    <el-dialog v-model="playlistDialogVisible" title="新建播放列表" width="400px" style="border-radius: 12px;">
      <el-input v-model="newPlaylistName" placeholder="输入列表名称" /><template #footer><el-button type="primary" @click="handleCreatePlaylist">创建</el-button></template>
    </el-dialog>
    <el-dialog v-model="viewPlaylistDialogVisible" width="1000px" :show-close="true" class="yt-playlist-dialog" align-center>
       <!-- 这里省略播放列表详情的复杂 HTML，请直接使用上一版的内容 -->
       <div class="yt-pl-layout">
        <div class="yt-pl-sidebar" :style="{ backgroundImage: `url(${currentPlaylist?.cover_url})` }">
           <div class="yt-pl-bg-blur"></div>
           <div class="yt-pl-content">
              <div class="yt-pl-cover-box"><img :src="currentPlaylist?.cover_url" class="yt-pl-cover-img"></div>
              <h2 class="yt-pl-title">{{ currentPlaylist?.title }}</h2>
              <div class="yt-pl-owner">{{ author.username }}</div>
              <div class="yt-pl-actions">
                 <el-button type="primary" round class="play-all-btn" v-if="currentPlaylistVideos.length > 0" @click="goToVideo(currentPlaylistVideos[0].id, currentPlaylist.id)"><el-icon style="margin-right:5px"><VideoPlay /></el-icon> 播放全部</el-button>
                 <el-button type="primary" round class="play-all-btn" v-if="isOwner" @click="addToPlVisible = true"><el-icon style="margin-right:5px"><Plus /></el-icon> 添加视频</el-button>
                 <el-button type="danger" round class="play-all-btn delete-btn" v-if="isOwner" @click="handleDeletePlaylist(currentPlaylist.id)"><el-icon style="margin-right:5px"><Delete /></el-icon> 删除列表</el-button>
              </div>
           </div>
        </div>
        <div class="yt-pl-list-container">
          <div v-if="currentPlaylistVideos.length > 0"><div v-for="(v, index) in currentPlaylistVideos" :key="v.id" class="yt-pl-item" @click="goToVideo(v.id, currentPlaylist.id)"><div class="yt-pl-index">{{ index + 1 }}</div><div class="yt-pl-thumb-box"><img :src="v.cover_url" class="yt-pl-thumb"></div><div class="yt-pl-info"><div class="yt-pl-v-title">{{ v.title }}</div></div><div class="yt-pl-item-action" v-if="isOwner" @click.stop="handleRemoveVideo(v.id)"><el-icon><Delete /></el-icon></div></div></div>
          <el-empty v-else description="为空" />
        </div>
      </div>
    </el-dialog>
    <el-dialog v-model="addToPlVisible" title="选择视频加入列表" width="500px" style="border-radius: 12px;">
      <div class="mini-video-list"><div v-for="v in videoList" :key="v.id" class="mini-video-item" @click="addVideoToPl(v.id)"><img :src="v.cover_url" /><span>{{ v.title }}</span><el-icon><Plus /></el-icon></div></div>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
import { getChannelInfo, toggleFollow, updateProfile, uploadAvatar, uploadBanner } from '../api/user';
import { createPlaylist, deletePlaylist, addVideoToPlaylist, getPlaylistVideos, removeVideoFromPlaylist } from '../api/playlist'; 
import { deleteVideo } from '../api/video';
import { Search, Plus, List, VideoPlay, Camera, Delete } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
// 引入裁剪组件
import ImageCropper from '../components/ImageCropper.vue';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const authorId = route.params.id || userStore.userInfo.id;
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
const viewPlaylistDialogVisible = ref(false);
const addToPlVisible = ref(false);

// 裁剪相关
const avatarInput = ref(null);
const bannerInput = ref(null);
const avatarCropperRef = ref(null);
const bannerCropperRef = ref(null);

const editForm = ref({ username: '', description: '' });
const newPlaylistName = ref('');
const currentPlaylist = ref(null);
const currentPlaylistVideos = ref([]);

const isOwner = computed(() => userStore.token && String(userStore.userInfo.id) === String(route.params.id));

const bannerStyle = computed(() => ({
  backgroundImage: author.value.banner ? `url(${author.value.banner})` : 'linear-gradient(90deg, #cc2b5e 0%, #753a88 100%)',
  backgroundSize: 'cover',
  backgroundPosition: 'center'
}));

const loadData = async () => {
  try {
    const res = await getChannelInfo({
      author_id: route.params.id || userStore.userInfo.id,
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

// --- 裁剪与上传核心逻辑 ---
const triggerAvatarSelect = () => avatarInput.value.click();
const triggerBannerSelect = () => bannerInput.value.click();

const onFileSelect = (e, type) => {
  const file = e.target.files[0];
  if (!file) return;
  
  // 打开对应的裁剪弹窗
  if (type === 'avatar') {
    avatarCropperRef.value.open(file);
  } else {
    bannerCropperRef.value.open(file);
  }
  // 清空 input，允许重复选同一文件
  e.target.value = ''; 
};

const doUploadAvatar = async (blob, done) => {
  const formData = new FormData();
  formData.append('file', blob, 'avatar.jpg');
  try {
    const res = await uploadAvatar(formData);
    if (res.data.code === 200) {
      author.value.avatar = res.data.url;
      userStore.setLoginState(userStore.token, { ...userStore.userInfo, avatar: res.data.url }); // 更新全局 Store
      ElMessage.success('头像更新成功');
      done(); // 关闭弹窗
    } else {
      ElMessage.error(res.data.msg);
    }
  } catch (e) { ElMessage.error('上传失败'); }
};

const doUploadBanner = async (blob, done) => {
  const formData = new FormData();
  formData.append('file', blob, 'banner.jpg');
  try {
    const res = await uploadBanner(formData);
    if (res.data.code === 200) {
      author.value.banner = res.data.url;
      ElMessage.success('横幅更新成功');
      done();
    }
  } catch (e) { ElMessage.error('上传失败'); }
};

// --- 其他业务逻辑 ---
const handleSubscribe = async () => { if (!userStore.token) return ElMessage.warning('请先登录'); try { const res = await toggleFollow({ follower_id: userStore.userInfo.id, followed_id: route.params.id }); if (res.data.code === 200) { stats.value.is_following = res.data.is_following; stats.value.fans = res.data.fans_count; ElMessage.success(res.data.is_following ? '订阅成功' : '已取消订阅'); } } catch (e) { ElMessage.error('操作失败'); } };
const openPlaylistDialog = () => { newPlaylistName.value = ''; playlistDialogVisible.value = true; };
const handleCreatePlaylist = async () => { if (!newPlaylistName.value) return; const res = await createPlaylist({ title: newPlaylistName.value, user_id: userStore.userInfo.id }); if (res.data.code === 200) { ElMessage.success('创建成功'); loadData(); playlistDialogVisible.value = false; } };
const handleDeletePlaylist = (id) => { ElMessageBox.confirm('确定删除？', '提示').then(async () => { await deletePlaylist(id); loadData(); viewPlaylistDialogVisible.value = false; }); };
const handleViewPlaylist = async (pl) => { currentPlaylist.value = pl; try { const res = await getPlaylistVideos(pl.id); if (res.data.code === 200) { currentPlaylistVideos.value = res.data.data; viewPlaylistDialogVisible.value = true; } } catch (e) { ElMessage.error('获取列表失败'); } };
const goToVideo = (vid, pid) => { if(pid) router.push({ path: `/video/${vid}`, query: { list: pid } }); else router.push(`/video/${vid}`); };
const addVideoToPl = async (vid) => { const res = await addVideoToPlaylist({ playlist_id: currentPlaylist.value.id, video_id: vid }); if (res.data.code === 200) { ElMessage.success(res.data.msg); addToPlVisible.value = false; const refreshRes = await getPlaylistVideos(currentPlaylist.value.id); currentPlaylistVideos.value = refreshRes.data.data; loadData(); } };
const handleRemoveVideo = async (vid) => { try { const res = await removeVideoFromPlaylist({ playlist_id: currentPlaylist.value.id, video_id: vid }); if (res.data.code === 200) { ElMessage.success('已移除'); currentPlaylistVideos.value = currentPlaylistVideos.value.filter(v => v.id !== vid); loadData(); } } catch (e) { ElMessage.error('移除失败'); } };
const openEditDialog = () => { editForm.value = { username: author.value.username, description: author.value.description }; editDialogVisible.value = true; };
const saveProfile = async () => { const res = await updateProfile({ user_id: userStore.userInfo.id, ...editForm.value }); if (res.data.code === 200) { ElMessage.success('保存成功'); author.value.username = res.data.data.username; author.value.description = res.data.data.description; userStore.setLoginState(userStore.token, res.data.data); editDialogVisible.value = false; } };
const handleDeleteVideo = (id) => { ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' }).then(async () => { await deleteVideo(id); loadData(); ElMessage.success('删除成功'); }); };

watch(() => route.params.id, (newId) => { if(newId) { activeTab.value = 'videos'; searchQuery.value = ''; sortBy.value = 'new'; videoList.value = []; playlists.value = []; loadData(); } });
onMounted(() => loadData());
</script>

<style scoped>
/* 保持原有样式，添加裁剪框容器样式 */
.channel-container { background: #fff; min-height: 100vh; padding-bottom: 40px; }
.channel-layout { max-width: 1284px; margin: 0 auto; padding: 0 24px; }
.channel-banner { height: 210px; background-color: #eee; border-radius: 16px; margin-top: 20px; position: relative; overflow: hidden; }
.channel-banner.is-owner { cursor: pointer; }
.edit-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; gap: 8px; opacity: 0; transition: opacity 0.2s; }
.channel-banner.is-owner:hover .edit-overlay { opacity: 1; }
.header-content { padding: 0 10px; display: flex; align-items: flex-start; margin-top: 16px; margin-bottom: 20px; }
.avatar-section { margin-right: 24px; position: relative; border-radius: 50%; padding: 2px; }
.avatar-section.is-owner { cursor: pointer; }
.channel-avatar { border: 1px solid #eee; }
.avatar-edit-mask { position: absolute; top: 0; left: 0; right: 0; bottom: 0; border-radius: 50%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; opacity: 0; transition: opacity 0.2s; }
.avatar-section.is-owner:hover .avatar-edit-mask { opacity: 1; }
.info-section { padding-top: 10px; flex: 1; }
.channel-name { font-size: 28px; font-weight: bold; margin: 0 0 5px 0; color: #0f0f0f; }
.channel-meta { color: #606060; font-size: 14px; margin-bottom: 10px; display: flex; gap: 10px; }
.channel-desc { color: #606060; font-size: 14px; margin-bottom: 15px; max-width: 600px; white-space: pre-wrap; }
.yt-sub-btn { background: #0f0f0f; color: #fff; border: none; padding: 0 16px; height: 36px; border-radius: 18px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; }
.yt-sub-btn:hover { background: #272727; }
.yt-sub-btn.subscribed { background: #f2f2f2; color: #0f0f0f; }
.owner-actions { display: flex; gap: 10px; }
.action-btn { background: #f2f2f2; border: none; color: #0f0f0f; font-weight: 500; }
.action-btn:hover { background: #e5e5e5; }
.channel-nav { display: flex; justify-content: space-between; align-items: center; height: 48px; }
.nav-tabs { display: flex; gap: 30px; height: 100%; }
.nav-tab { font-size: 16px; font-weight: 500; color: #606060; cursor: pointer; display: flex; align-items: center; border-bottom: 3px solid transparent; }
.nav-tab.active { color: #0f0f0f; border-bottom-color: #0f0f0f; }
.nav-filters { display: flex; align-items: center; gap: 10px; }
.channel-search { display: flex; align-items: center; gap: 5px; font-size: 14px; border-bottom: 1px solid #ccc; padding: 0 5px; }
.channel-search input { border: none; outline: none; width: 100px; font-size: 14px; background: transparent; }
.content-section { padding: 24px 0; }
.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 20px; row-gap: 30px; }
.video-card { cursor: pointer; transition: transform 0.2s; }
.thumbnail-wrapper { width: 100%; aspect-ratio: 16/9; background: #eee; border-radius: 12px; overflow: hidden; position: relative; margin-bottom: 10px; }
.thumbnail { width: 100%; height: 100%; object-fit: cover; transition: transform 0.2s; }
.video-card:hover .thumbnail { transform: scale(1.05); }
.duration { position: absolute; bottom: 5px; right: 5px; background: rgba(0,0,0,0.8); color: white; padding: 2px 4px; border-radius: 4px; font-size: 12px; }
.video-title { font-size: 14px; font-weight: 600; line-height: 1.4; color: #0f0f0f; margin: 0 0 4px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.video-meta { font-size: 12px; color: #606060; }
.playlist-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 20px; }
.playlist-card-new { cursor: pointer; }
.pl-thumb-container { position: relative; width: 100%; aspect-ratio: 16/9; margin-bottom: 10px; }
.pl-stack-layer { position: absolute; top: -4px; left: 50%; transform: translateX(-50%); width: 90%; height: 4px; background: #d0d0d0; border-radius: 4px 4px 0 0; z-index: 0; }
.pl-thumb-wrapper { position: relative; width: 100%; height: 100%; border-radius: 12px; overflow: hidden; background: #eee; z-index: 1; }
.pl-img { width: 100%; height: 100%; object-fit: cover; }
.pl-count-bar { position: absolute; bottom: 0; left: 0; right: 0; height: 28px; background: rgba(0,0,0,0.7); color: white; display: flex; align-items: center; justify-content: center; gap: 6px; font-size: 12px; backdrop-filter: blur(2px); }
.pl-hover-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; opacity: 0; transition: opacity 0.2s; }
.playlist-card-new:hover .pl-hover-overlay { opacity: 1; }
.pl-info-new .pl-title-new { font-weight: 600; font-size: 14px; color: #0f0f0f; margin-bottom: 4px; }
.pl-link-text { font-size: 12px; color: #606060; font-weight: 600; margin-bottom: 4px; }

/* 弹窗布局 */
.yt-pl-layout { display: flex; height: 500px; overflow: hidden; }
.yt-pl-sidebar { width: 360px; flex-shrink: 0; padding: 24px; position: relative; overflow: hidden; background-size: cover; background-position: center; display: flex; flex-direction: column; color: white; }
.yt-pl-bg-blur { position: absolute; top: 0; left: 0; right: 0; bottom: 0; backdrop-filter: blur(40px) brightness(0.6); background: rgba(0,0,0,0.5); z-index: 0; }
.yt-pl-content { position: relative; z-index: 1; display: flex; flex-direction: column; height: 100%; }
.yt-pl-cover-box { width: 100%; aspect-ratio: 16/9; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.2); margin-bottom: 20px; }
.yt-pl-cover-img { width: 100%; height: 100%; object-fit: cover; }
.yt-pl-title { font-size: 24px; font-weight: bold; margin: 0 0 10px 0; }
.yt-pl-owner { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
.yt-pl-meta { font-size: 12px; margin-bottom: 20px; opacity: 0.9; }
.yt-pl-actions { margin-top: auto; display: flex; flex-direction: column; gap: 10px; }
.play-all-btn { width: 100%; background: white; color: black; border: none; font-weight: 600; }
.play-all-btn:hover { background: #eee; color: black; }
.play-all-btn.delete-btn { background: #ff4d4f; color: white; }
.play-all-btn.delete-btn:hover { background: #ff7875; }
.yt-pl-list-container { flex: 1; background: #fff; overflow-y: auto; padding: 10px 0; }
.yt-pl-item { display: flex; align-items: center; padding: 10px 20px; cursor: pointer; transition: background 0.1s; position: relative; }
.yt-pl-item:hover { background: #f2f2f2; }
.yt-pl-index { width: 30px; color: #606060; font-size: 14px; }
.yt-pl-thumb-box { width: 120px; height: 68px; border-radius: 8px; overflow: hidden; margin-right: 15px; flex-shrink: 0; }
.yt-pl-thumb { width: 100%; height: 100%; object-fit: cover; }
.yt-pl-info { flex: 1; min-width: 0; }
.yt-pl-v-title { font-size: 14px; font-weight: 600; color: #0f0f0f; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.yt-pl-v-meta { font-size: 12px; color: #606060; }
.yt-pl-item-action { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); opacity: 0; transition: opacity 0.2s; color: #606060; padding: 8px; border-radius: 50%; }
.yt-pl-item:hover .yt-pl-item-action { opacity: 1; }
.yt-pl-item-action:hover { background: #e5e5e5; color: #ff4d4f; }
:deep(.yt-playlist-dialog .el-dialog__body) { padding: 0; }
:deep(.yt-playlist-dialog .el-dialog__header) { display: none; }
.mini-video-list { max-height: 300px; overflow-y: auto; }
.mini-video-item { display: flex; align-items: center; gap: 10px; padding: 8px; cursor: pointer; border-bottom: 1px solid #eee; }
.mini-video-item:hover { background: #f5f7fa; }
.mini-video-item img { width: 60px; height: 34px; object-fit: cover; border-radius: 2px; }
.mini-video-item span { flex: 1; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>