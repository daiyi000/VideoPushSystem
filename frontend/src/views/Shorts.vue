<template>
  <div class="shorts-container">
    <div class="shorts-viewport" @wheel="handleWheel">
      
      <!-- 上一个视频按钮 -->
      <div class="nav-btn prev" @click="prevVideo" v-if="currentIndex > 0">
        <el-icon><ArrowUp /></el-icon>
      </div>

      <!-- 核心布局：[左侧信息] - [中间视频] - [右侧按钮] - [扩展面板] -->
      <div class="shorts-content-layout" v-if="currentVideo">
        
        <!-- 1. 左侧：作者与标题信息 -->
        <div class="left-side-info">
          
          <!-- 作者卡片 -->
          <div class="info-card author-card" @click.stop="$router.push(`/@${currentVideo.uploader_name}`)">
             <el-avatar :size="56" :src="currentVideo.uploader_avatar" class="author-avatar" />
             <div class="author-details">
                <div class="author-name">@{{ currentVideo.uploader_name }}</div>
                <div class="sub-hint">查看频道</div>
             </div>
             <button 
                class="yt-sub-btn" 
                :class="{ subscribed: isFollowing }"
                @click.stop="handleSubscribe"
              >
                {{ isFollowing ? '已订阅' : '订阅' }}
              </button>
          </div>

          <!-- 标题卡片 -->
          <div class="info-card title-card" @click="togglePanel('details')" :class="{ active: activePanel === 'details' }">
             <h2 class="video-title">
               {{ currentVideo.title }}
             </h2>
             <div class="click-hint">
               <el-icon><InfoFilled /></el-icon> 查看简介
             </div>
          </div>
          
        </div>

        <!-- 2. 中间：视频播放器 -->
        <transition :name="transitionDirection" mode="out-in">
          <div class="short-player-wrapper" :key="currentVideo.id">
            <video 
              ref="videoRef"
              :src="currentVideo.url" 
              class="short-video"
              autoplay 
              loop 
              @click="togglePlay"
              @timeupdate="onTimeUpdate"
            ></video>
            
            <!-- 播放/暂停遮罩 -->
            <div class="play-mask" v-if="!isPlaying" @click="togglePlay">
              <div class="play-icon-bg"><el-icon size="48"><VideoPlay /></el-icon></div>
            </div>

            <!-- 进度条 -->
            <div class="progress-bar-container">
               <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
            </div>
          </div>
        </transition>

        <!-- 3. 右侧：互动操作栏 -->
        <div class="actions-side">
           <div class="action-item">
             <div class="action-btn" @click="handleLike">
               <div class="icon-circle" :class="{ active: interaction.is_like }">
                  <el-icon size="28">
                      <!-- 已点赞：实心 -->
                      <svg v-if="interaction.is_like" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-1.91l-.01-.01L23 10z"/>
                      </svg>
                      <!-- 未点赞：空心 (黑边) -->
                      <svg v-else viewBox="0 0 24 24" fill="transparent" stroke="currentColor" stroke-width="2">
                         <path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-1.91l-.01-.01L23 10z"/>
                      </svg>
                  </el-icon>
               </div>
               <span class="action-label">{{ formatCount(currentVideo.likes) }}</span>
             </div>
           </div>

           <div class="action-item">
             <div class="action-btn" @click="togglePanel('comments')">
               <div class="icon-circle" :class="{ active: activePanel === 'comments' }">
                 <el-icon size="24"><ChatDotRound /></el-icon>
               </div>
               <span class="action-label">{{ commentCount || '评论' }}</span>
             </div>
           </div>

           <div class="action-item">
             <div class="action-btn" @click="handleShare">
               <div class="icon-circle"><el-icon size="24"><Share /></el-icon></div>
               <span class="action-label">分享</span>
             </div>
           </div>
        </div>

        <!-- 4. 扩展面板 (最右侧，显示简介或评论) -->
        <transition name="slide-panel">
          <div class="expand-panel" v-if="activePanel !== 'none'">
             <div class="panel-header-row">
                <span class="panel-title">{{ activePanel === 'details' ? '简介' : '评论' }}</span>
                <el-icon class="panel-close" @click="activePanel = 'none'"><Close /></el-icon>
             </div>
             
             <!-- A. 详情内容 -->
             <div v-if="activePanel === 'details'" class="details-content">
                <div class="detail-stats">
                   <div class="stat-item">
                     <div class="val">{{ formatCount(currentVideo.views) }}</div>
                     <div class="lbl">观看次数</div>
                   </div>
                   <div class="stat-item">
                     <div class="val">{{ formatDate(currentVideo.upload_time) }}</div>
                     <div class="lbl">发布时间</div>
                   </div>
                </div>
                <el-divider style="margin: 15px 0" />
                <div class="detail-desc">{{ currentVideo.description || '暂无简介' }}</div>
                <div class="detail-tags" v-if="currentVideo.tags">
                   <span v-for="tag in currentVideo.tags.split(',')" :key="tag" class="hash-tag">#{{ tag }}</span>
                </div>
             </div>

             <!-- B. 评论内容 -->
             <div v-if="activePanel === 'comments'" class="comments-content">
                <div class="comment-sort-bar">
                   <span :class="{ active: sortType === 'hot' }" @click="changeSort('hot')">最热</span>
                   <el-divider direction="vertical" />
                   <span :class="{ active: sortType === 'new' }" @click="changeSort('new')">最新</span>
                </div>
                
                <div class="c-list-scroll">
                  <div v-for="c in commentsList" :key="c.id" class="comment-item">
                     <el-avatar :size="32" :src="c.user.avatar" />
                     <div class="comment-content">
                       <div class="c-user">
                          {{ c.user.username }} 
                          <span class="c-time">{{ formatDate(c.time) }}</span>
                       </div>
                       <div class="c-text">{{ c.content }}</div>
                     </div>
                  </div>
                  <el-empty v-if="commentsList.length === 0" description="还没有评论" :image-size="60" />
                </div>

                <div class="c-input-area">
                   <el-input v-model="commentText" placeholder="发表评论..." @keyup.enter="postComment">
                      <template #append>
                         <el-button @click="postComment"><el-icon><Position /></el-icon></el-button>
                      </template>
                   </el-input>
                </div>
             </div>
          </div>
        </transition>

      </div>

      <!-- 下一个视频按钮 -->
      <div class="nav-btn next" @click="nextVideo">
        <el-icon><ArrowDown /></el-icon>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
import { getVideoDetail, getVideoList, postAction, checkFavStatus } from '../api/video';
import { getComments, sendComment, checkInteractionStatus } from '../api/interaction';
import { toggleFollow, getChannelInfo } from '../api/user';
import { ArrowUp, ArrowDown, VideoPlay, ChatDotRound, Share, Close, Position, InfoFilled } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const videoList = ref([]);
const currentIndex = ref(0);
const currentVideo = ref(null);
const videoRef = ref(null);
const isPlaying = ref(true);
const progressPercent = ref(0);

const interaction = ref({ is_fav: false, is_like: false });
const isFollowing = ref(false);

const activePanel = ref('none'); // 'none' | 'details' | 'comments'
const commentsList = ref([]);
const commentCount = ref(0);
const commentText = ref('');
const sortType = ref('hot'); 

const transitionDirection = ref('slide-up');
const isScrolling = ref(false);

const loadShorts = async () => {
  try {
    const res = await getVideoList(); 
    if (res.data.code === 200) {
      const allVideos = res.data.data;
      videoList.value = allVideos.filter(v => v.is_short); 
      
      const initialId = route.params.id;
      // 随机播放
      if (!initialId || initialId === 'random') {
          if (videoList.value.length > 0) {
              // 随机选一个起始点，增加趣味性
              currentIndex.value = Math.floor(Math.random() * videoList.value.length);
              playCurrent();
          }
          return;
      }

      // 指定ID播放
      if (initialId) {
        const idx = videoList.value.findIndex(v => String(v.id) === String(initialId));
        if (idx !== -1) {
            currentIndex.value = idx;
        } else {
          try {
             const detail = await getVideoDetail(initialId);
             if (detail.data.code === 200) {
                 videoList.value.unshift(detail.data.data);
                 currentIndex.value = 0;
             }
          } catch(e) {}
        }
      }
      if (videoList.value.length > 0) playCurrent();
    }
  } catch (e) { console.error(e); }
};

const playCurrent = async () => {
  if (!videoList.value[currentIndex.value]) return;
  
  // 1. 设置当前视频基础信息
  currentVideo.value = videoList.value[currentIndex.value];
  interaction.value = { is_fav: false, is_like: false };
  isFollowing.value = false;
  progressPercent.value = 0;
  activePanel.value = 'none'; 
  
  // 2. 更新 URL
  router.replace(`/shorts/${currentVideo.value.id}`);

  // 3. 【修复】重新请求视频详情以获取最新点赞数
  try {
    const detailRes = await getVideoDetail(currentVideo.value.id);
    if (detailRes.data.code === 200) {
        // 更新点赞数等实时数据
        currentVideo.value.likes = detailRes.data.data.likes;
        // 如果后端有返回，也更新关注信息
    }
  } catch(e) {}

  // 4. 加载评论
  getComments(currentVideo.value.id).then(res => {
      commentsList.value = res.data.data;
      commentCount.value = res.data.data.length;
  });

  // 5. 加载用户状态 (点赞/关注)
  if (userStore.token) {
      // 检查点赞
      const statusRes = await checkInteractionStatus(userStore.userInfo.id, currentVideo.value.id);
      if(statusRes.data.code === 200) {
        interaction.value = statusRes.data.data;
      }
      // 记录观看
      postAction({ user_id: userStore.userInfo.id, video_id: currentVideo.value.id, type: 'view' });

      // 检查关注
      try {
        const channelRes = await getChannelInfo({
            author_id: currentVideo.value.uploader_id,
            visitor_id: userStore.userInfo.id
        });
        if (channelRes.data.code === 200) {
            isFollowing.value = channelRes.data.data.stats.is_following;
        }
      } catch (e) { console.error("获取关注状态失败", e); }
  }

  // 6. 播放视频
  if (videoRef.value) {
    videoRef.value.src = currentVideo.value.url;
    videoRef.value.play().catch(() => { isPlaying.value = false; });
    isPlaying.value = true;
  }
};

// ... 其他逻辑保持不变 ...
const handleSubscribe = async () => { if (!userStore.token) return ElMessage.warning('请先登录'); if (String(userStore.userInfo.id) === String(currentVideo.value.uploader_id)) return ElMessage.warning('不能订阅自己'); try { const res = await toggleFollow({ follower_id: userStore.userInfo.id, followed_id: currentVideo.value.uploader_id }); if (res.data.code === 200) { isFollowing.value = res.data.is_following; ElMessage.success(res.data.is_following ? '订阅成功' : '已取消订阅'); } } catch (e) { ElMessage.error('操作失败'); } };
const togglePlay = () => { if (videoRef.value.paused) { videoRef.value.play(); isPlaying.value = true; } else { videoRef.value.pause(); isPlaying.value = false; } };
const onTimeUpdate = () => { if (videoRef.value) { const current = videoRef.value.currentTime; const total = videoRef.value.duration; progressPercent.value = (current / total) * 100; } };
const nextVideo = () => { if (currentIndex.value < videoList.value.length - 1) { transitionDirection.value = 'slide-up'; currentIndex.value++; } else { ElMessage.info('没有更多视频了'); } };
const prevVideo = () => { if (currentIndex.value > 0) { transitionDirection.value = 'slide-down'; currentIndex.value--; } };
const handleWheel = (e) => { if (isScrolling.value) return; if (e.deltaY > 30) { nextVideo(); lockScroll(); } else if (e.deltaY < -30) { prevVideo(); lockScroll(); } };
const lockScroll = () => { isScrolling.value = true; setTimeout(() => { isScrolling.value = false; }, 800); };
const handleKeydown = (e) => { if (e.key === 'ArrowDown') nextVideo(); if (e.key === 'ArrowUp') prevVideo(); if (e.key === ' ') togglePlay(); };

const handleLike = async () => {
    if (!userStore.token) return ElMessage.warning('请先登录');
    const type = interaction.value.is_like ? 'unlike' : 'like';
    interaction.value.is_like = !interaction.value.is_like;
    // 实时更新数字
    if (interaction.value.is_like) currentVideo.value.likes++;
    else if (currentVideo.value.likes > 0) currentVideo.value.likes--;
    await postAction({ user_id: userStore.userInfo.id, video_id: currentVideo.value.id, type });
};

const togglePanel = (panelName) => { if (activePanel.value === panelName) { activePanel.value = 'none'; } else { activePanel.value = panelName; if (panelName === 'comments') loadComments(); } };
const loadComments = async () => { const res = await getComments(currentVideo.value.id, sortType.value); commentsList.value = res.data.data; commentCount.value = res.data.data.length; };
const changeSort = (type) => { sortType.value = type; loadComments(); };
const postComment = async () => { if (!userStore.token) return ElMessage.warning('请先登录'); if (!commentText.value) return; await sendComment({ user_id: userStore.userInfo.id, video_id: currentVideo.value.id, content: commentText.value }); commentText.value = ''; loadComments(); };
const handleShare = () => { const url = window.location.href; navigator.clipboard.writeText(url).then(() => { ElMessage.success('链接已复制'); }); };
const formatCount = (num) => { if (!num) return 0; return num > 10000 ? (num/10000).toFixed(1) + '万' : num; }
const formatDate = (str) => str ? str.split(' ')[0] : '';

watch(() => currentIndex.value, playCurrent);

onMounted(() => {
  loadShorts();
  window.addEventListener('keydown', handleKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.shorts-container {
  position: fixed; top: 56px; left: 0; width: 100vw; height: calc(100vh - 56px);
  display: flex; justify-content: center;
  background: transparent;
  overflow: hidden; z-index: 1;
}

.shorts-viewport {
  width: 100%; height: 100%; position: relative;
  display: flex; align-items: center; justify-content: center;
  margin-top: 20px;
}

.shorts-content-layout {
  display: flex; align-items: flex-end; justify-content: center;
  gap: 16px; height: 90%; position: relative;
}

/* 左侧信息 */
.left-side-info {
  width: 320px; display: flex; flex-direction: column; justify-content: center; /* 垂直居中 */
  height: 100%; gap: 16px; z-index: 5;
}

.author-card, .title-card {
  background: #fff; padding: 16px; border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  width: 100%;
}
.author-card { display: flex; flex-direction: column; gap: 12px; }
.author-top { display: flex; align-items: center; gap: 12px; cursor: pointer; }
.author-name { font-weight: bold; font-size: 15px; color: #0f0f0f; }
.sub-text { font-size: 12px; color: #606060; }

.title-card.clickable { cursor: pointer; transition: transform 0.2s; }
.title-card:hover { transform: translateY(-2px); }
.title-card.active { border: 2px solid #000; }
.video-title { font-size: 16px; font-weight: 600; line-height: 1.4; color: #0f0f0f; margin: 0 0 8px 0; }
.click-hint { font-size: 12px; color: #606060; display: flex; align-items: center; gap: 4px; }

/* 中间播放器 */
.short-player-wrapper {
  width: 450px; aspect-ratio: 9 / 16; height: auto; max-height: 96%;
  background: #000; border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.15); position: relative; flex-shrink: 0;
}
.short-video { width: 100%; height: 100%; object-fit: cover; }

/* 右侧按钮 */
.actions-side {
  display: flex; flex-direction: column; gap: 24px;
  justify-content: flex-end; height: 90%; padding-bottom: 40px;
}
.action-item { display: flex; align-items: center; }
.action-btn { display: flex; flex-direction: column; align-items: center; gap: 6px; cursor: pointer; }
.icon-circle { 
  width: 52px; height: 52px; background: #f2f2f2; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #0f0f0f; transition: all 0.2s;
}
.action-btn:hover .icon-circle { background: #e5e5e5; transform: scale(1.1); }
/* 激活状态：黑底白字 */
.icon-circle.active { background: #0f0f0f; color: #fff; } 
.action-label { color: #0f0f0f; font-size: 13px; font-weight: 500; }

/* 扩展面板 */
.expand-panel {
  width: 360px; height: 96%; background: #fff; border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  display: flex; flex-direction: column; overflow: hidden;
  margin-left: 10px; animation: slideIn 0.3s ease;
}
@keyframes slideIn { from { width: 0; opacity: 0; } to { width: 360px; opacity: 1; } }
.panel-header-row { display: flex; justify-content: space-between; align-items: center; padding: 15px; border-bottom: 1px solid #eee; background: #f9f9f9; }
.panel-title { font-weight: bold; font-size: 16px; }
.panel-close { cursor: pointer; font-size: 20px; padding: 5px; }

/* 详情/评论内容区 */
.details-content { padding: 20px; overflow-y: auto; flex: 1; }
.detail-stats { display: flex; justify-content: space-around; text-align: center; }
.val { font-weight: bold; font-size: 18px; }
.lbl { font-size: 12px; color: #606060; }
.detail-desc { font-size: 14px; line-height: 1.5; white-space: pre-wrap; margin-bottom: 20px; }
.hash-tag { color: #065fd4; margin-right: 5px; cursor: pointer; }
.comments-content { display: flex; flex-direction: column; height: 100%; }
.comment-sort-bar { padding: 10px 15px; border-bottom: 1px solid #eee; font-size: 13px; font-weight: 500; }
.c-list-scroll { flex: 1; overflow-y: auto; padding: 15px; }
.comment-item { display: flex; gap: 10px; margin-bottom: 15px; }
.c-user { font-size: 13px; font-weight: bold; color: #606060; margin-bottom: 4px; }
.c-time { font-size: 12px; color: #909090; margin-left: 8px; font-weight: normal; }
.c-text { font-size: 14px; color: #0f0f0f; line-height: 1.4; }
.c-input-area { padding: 15px; border-top: 1px solid #eee; background: #fff; }

/* 导航箭头 */
.nav-btn { position: absolute; left: 50%; transform: translateX(-50%); width: 48px; height: 48px; background: rgba(0,0,0,0.05); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #333; z-index: 10; transition: all 0.2s; }
.nav-btn:hover { background: rgba(0,0,0,0.1); transform: translateX(-50%) scale(1.1); }
.nav-btn.prev { top: -30px; }
.nav-btn.next { bottom: -30px; right: -80px; left: auto; transform: none; }

.play-mask { position: absolute; top:0; left:0; right:0; bottom:0; display:flex; align-items:center; justify-content:center; background: rgba(0,0,0,0.2); }
.play-icon-bg { background: rgba(0,0,0,0.6); border-radius: 50%; padding: 15px; display: flex; color: white; }
.progress-bar-container { position: absolute; bottom: 0; left: 0; right: 0; height: 3px; background: rgba(255,255,255,0.3); }
.progress-bar { height: 100%; background: #ff0000; transition: width 0.1s linear; }

.yt-sub-btn { background: #0f0f0f; color: #fff; border: none; padding: 0 16px; height: 36px; border-radius: 18px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; width: 100%; }
.yt-sub-btn:hover { background: #272727; }
.yt-sub-btn.subscribed { background: #f2f2f2; color: #0f0f0f; }
.yt-sub-btn.subscribed:hover { background: #e5e5e5; }
</style>