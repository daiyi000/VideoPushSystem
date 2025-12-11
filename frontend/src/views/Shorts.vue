<template>
  <div class="shorts-container">
    <div class="shorts-viewport" @wheel="handleWheel">
      
      <div class="nav-btn prev" @click="prevVideo" v-if="currentIndex > 0">
        <el-icon><ArrowUp /></el-icon>
      </div>

      <div class="shorts-content-layout" v-if="currentVideo">
        
        <div class="left-side-info">
          <div class="info-pill title-pill" @click="togglePanel('details')" :class="{ active: activePanel === 'details' }">
             <div class="pill-content">
               <h2 class="video-title text-ellipsis">{{ currentVideo.title }}</h2>
               <el-icon class="icon-right"><InfoFilled /></el-icon>
             </div>
          </div>

          <div class="info-pill author-pill" @click.stop="$router.push(`/@${currentVideo.uploader_name}`)">
             <div class="author-row">
                <el-avatar :size="40" :src="currentVideo.uploader_avatar" class="author-avatar" />
                <div class="author-text">
                   <div class="author-name">@{{ currentVideo.uploader_name }}</div>
                </div>
             </div>
             <button 
                class="yt-sub-btn" 
                :class="{ subscribed: isFollowing }"
                @click.stop="handleSubscribe"
              >
                {{ isFollowing ? '已订阅' : '订阅' }}
              </button>
          </div>
        </div>

        <div class="center-column">
          <transition :name="transitionDirection">
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
              
              <div class="play-mask" v-if="!isPlaying" @click="togglePlay">
                <div class="play-icon-bg"><el-icon size="56"><VideoPlay /></el-icon></div>
              </div>

              <div class="progress-bar-container" 
     ref="progressBarRef"
     @mousedown.stop="startDrag">
   <div class="progress-bg"></div> 
   <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
   <div class="progress-thumb" :style="{ left: progressPercent + '%' }"></div>
</div>
            </div>
          </transition>
        </div>

        <div class="actions-side">
           <div class="action-item">
             <div class="action-btn" @click="handleLike">
               <div class="icon-circle" :class="{ active: interaction.is_like }">
                 <el-icon size="26">
                     <svg v-if="interaction.is_like" viewBox="0 0 24 24" fill="currentColor" style="color: white;"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-1.91l-.01-.01L23 10z"/></svg>
                     <svg v-else viewBox="0 0 24 24" fill="white" stroke="black" stroke-width="1.5" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" /></svg>
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

        <transition name="slide-panel">
          <div class="expand-panel" v-if="activePanel !== 'none'">
              
              <div class="panel-header-row">
                 <span class="panel-title-switch">
                    <span :class="{ active: activePanel === 'details' }" @click="activePanel = 'details'">简介</span>
                    <span class="divider">/</span>
                    <span :class="{ active: activePanel === 'comments' }" @click="activePanel = 'comments'">评论</span>
                 </span>
                 <el-icon class="panel-close" @click="activePanel = 'none'"><Close /></el-icon>
              </div>
              
              <div class="panel-scroll-area">
                
                <div v-if="activePanel === 'details'" class="details-content">
                    <div class="meta-block">
                        <div class="panel-video-title">
                          {{ currentVideo.title }} 
                          <span v-for="tag in (currentVideo.tags || '').split(',')" :key="tag" class="hash-tag"> #{{ tag }}</span>
                        </div>
                        <div class="yt-stats-row">
                            <div class="s-item"><div class="s-val">{{ formatCount(currentVideo.likes) }}</div><div class="s-lbl">赞</div></div>
                            <div class="s-item"><div class="s-val">{{ Number(currentVideo.views).toLocaleString() }}</div><div class="s-lbl">观看次数</div></div>
                            <div class="s-item"><div class="s-val">{{ formatDate(currentVideo.upload_time) }}</div><div class="s-lbl">发布时间</div></div>
                        </div>
                    </div>
                    <el-divider style="margin: 15px 0" />
                    <div class="detail-desc">{{ currentVideo.description || '暂无简介' }}</div>
                </div>

                <div v-if="activePanel === 'comments'" class="comments-content">
                    <div class="comment-sort-bar">
                       <span class="sort-chip" :class="{ active: sortType === 'hot' }" @click="changeSort('hot')">最热</span>
                       <div class="divider">/</div>
                       <span class="sort-chip" :class="{ active: sortType === 'new' }" @click="changeSort('new')">最新</span>
                    </div>
                    
                    <div class="c-list">
                      <div v-for="c in commentsList" :key="c.id" class="comment-item">
                          <el-avatar :size="32" :src="c.user.avatar" class="c-avatar" />
                          <div class="comment-content">
                            
                            <div v-if="c.is_pinned" class="pinned-badge">
                               <el-icon><Top /></el-icon> 由 {{ currentVideo.uploader_name }} 置顶
                            </div>
                            
                           <div class="c-header">
                              <span class="c-user">@{{ c.user.username }}</span>
                              <span class="c-time">{{ formatDate(c.time) }}</span>
                           </div>
                           <div class="c-text">{{ c.content }}</div>
                           
                           <div class="c-actions">
                              <div class="c-act-btn" @click="handleLikeComment(c)" :class="{ 'liked': c.is_liked }">
                                  <el-icon><svg v-if="c.is_liked" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-1.91l-.01-.01L23 10z"/></svg><svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M9 21h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.58 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2zM9 9l4.34-4.34L12 10h9v2l-3 7H9V9zM1 9h4v12H1z"/></svg></el-icon>
                                  {{ c.likes || '' }}
                              </div>
                              <div class="c-act-btn" @click="openReply(c.id, c.user.username)">回复</div>
                              
                              <el-dropdown v-if="isOwner" trigger="click" @command="handlePin" size="small">
                                <span class="more-btn-wrapper">
                                   <el-icon class="more-icon"><MoreFilled /></el-icon>
                                </span>
                                <template #dropdown>
                                  <el-dropdown-menu>
                                    <el-dropdown-item :command="c.id">{{ c.is_pinned ? '取消置顶' : '置顶评论' }}</el-dropdown-item>
                                  </el-dropdown-menu>
                                </template>
                              </el-dropdown>
                           </div>
                           
                           <div v-if="replyTargetId === c.id" class="reply-box">
                              <div class="reply-target-tag">
                                 <span>回复 @{{ replyToUser }}</span>
                              </div>
                              <el-input v-model="replyText" size="small" placeholder="输入回复内容..." />
                              <div class="reply-acts">
                                 <el-button size="small" @click="replyTargetId = null">取消</el-button>
                                 <el-button type="primary" size="small" @click="postComment(c.id)">发送</el-button>
                              </div>
                           </div>
                           
                           <div v-if="c.replies && c.replies.length" class="replies-wrapper">
                              <div class="reply-toggle" @click="c.expanded = !c.expanded">
                                 <el-icon><CaretBottom v-if="!c.expanded" /><CaretTop v-else /></el-icon> 
                                 {{ c.replies.length }} 条回复
                              </div>
                              <div v-if="c.expanded" class="reply-list">
                                 <div v-for="r in c.replies" :key="r.id" class="comment-item sub-item">
                                    <el-avatar :size="24" :src="r.user.avatar" />
                                    <div class="comment-content">
                                       <div class="c-header"><span class="c-user">{{ r.user.username }}</span></div>
                                       <div class="c-text">{{ r.content }}</div>
                                    </div>
                                 </div>
                              </div>
                           </div>
                         </div>
                      </div>
                      <el-empty v-if="commentsList.length === 0" description="还没有评论" :image-size="60" />
                    </div>
                </div>

              </div>
              
              <div class="panel-footer" v-if="activePanel === 'comments'">
                 <el-input 
                    v-model="commentText" 
                    placeholder="发表友善的评论..." 
                    @keyup.enter="postComment(null)"
                    class="comment-input"
                 >
                    <template #append>
                       <el-button @click="postComment(null)" class="send-btn">
                          <el-icon><Position /></el-icon>
                       </el-button>
                    </template>
                 </el-input>
              </div>

          </div>
        </transition>

      </div>

      <div class="nav-btn next" @click="nextVideo">
        <el-icon><ArrowDown /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
import { getVideoDetail, getVideoList, postAction } from '../api/video';
import { getComments, sendComment, checkInteractionStatus, likeComment, pinComment } from '../api/interaction';
import { toggleFollow, getChannelInfo } from '../api/user';
import { ArrowUp, ArrowDown, VideoPlay, ChatDotRound, Share, Close, Position, InfoFilled, CaretBottom, CaretTop, MoreFilled, Top } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
const progressBarRef = ref(null); // 进度条容器引用
const isDragging = ref(false);    // 是否正在拖拽

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

const activePanel = ref('none'); 
const commentsList = ref([]);
const commentCount = ref(0);
const commentText = ref('');
const replyText = ref('');
const replyTargetId = ref(null);
const replyToUser = ref(''); // 【新增】存储被回复的用户名
const sortType = ref('hot'); 

const transitionDirection = ref('slide-up');
const isScrolling = ref(false);

const isOwner = computed(() => {
  if (!userStore.token || !currentVideo.value) return false;
  return String(userStore.userInfo.id) === String(currentVideo.value.uploader_id);
});

const loadShorts = async () => {
  try {
    const res = await getVideoList(); 
    if (res.data.code === 200) {
      const allVideos = res.data.data;
      videoList.value = allVideos.filter(v => v.is_short); 
      
      const initialId = route.params.id;
      if (!initialId || initialId === 'random') {
          if (videoList.value.length > 0) {
              currentIndex.value = Math.floor(Math.random() * videoList.value.length);
              playCurrent();
          }
          return;
      }

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
  
  currentVideo.value = videoList.value[currentIndex.value];
  currentVideo.value.likes = parseInt(currentVideo.value.likes) || 0;
  
  interaction.value = { is_fav: false, is_like: false };
  isFollowing.value = false;
  progressPercent.value = 0;
  activePanel.value = 'none'; 
  
  router.replace(`/shorts/${currentVideo.value.id}`);

  try {
    const detailRes = await getVideoDetail(currentVideo.value.id);
    if (detailRes.data.code === 200) {
        currentVideo.value.likes = detailRes.data.data.likes;
    }
  } catch(e) {}

  getComments(currentVideo.value.id).then(res => {
      commentsList.value = res.data.data.map(c => ({...c, expanded: false}));
      commentCount.value = res.data.data.length;
  });

  if (userStore.token) {
      const statusRes = await checkInteractionStatus(userStore.userInfo.id, currentVideo.value.id);
      if(statusRes.data.code === 200) {
        interaction.value = statusRes.data.data;
      }
      postAction({ user_id: userStore.userInfo.id, video_id: currentVideo.value.id, type: 'view' });

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

  setTimeout(() => {
      if (videoRef.value) {
        videoRef.value.src = currentVideo.value.url;
        videoRef.value.play().catch(() => { isPlaying.value = false; });
        isPlaying.value = true;
      }
  }, 0);
};

const handleSubscribe = async () => {
  if (!userStore.token) return ElMessage.warning('请先登录');
  if (String(userStore.userInfo.id) === String(currentVideo.value.uploader_id)) return ElMessage.warning('不能订阅自己');
  try {
    const res = await toggleFollow({ follower_id: userStore.userInfo.id, followed_id: currentVideo.value.uploader_id });
    if (res.data.code === 200) {
      isFollowing.value = res.data.is_following; 
      ElMessage.success(res.data.is_following ? '订阅成功' : '已取消订阅');
    }
  } catch (e) { ElMessage.error('操作失败'); }
};

const togglePlay = () => {
  if (videoRef.value.paused) {
    videoRef.value.play();
    isPlaying.value = true;
  } else {
    videoRef.value.pause();
    isPlaying.value = false;
  }
};

const onTimeUpdate = () => {
    if (videoRef.value && !isDragging.value) {
        const current = videoRef.value.currentTime;
        const total = videoRef.value.duration;
        progressPercent.value = (current / total) * 100;
    }
};

const startDrag = (e) => {
    isDragging.value = true;
    handleDrag(e); // 点击瞬间先更新一次
    document.addEventListener('mousemove', handleDrag);
    document.addEventListener('mouseup', stopDrag);
};

const handleDrag = (e) => {
    if (!videoRef.value || !progressBarRef.value) return;
    
    const rect = progressBarRef.value.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    // 计算百分比，限制在 0-1 之间
    const percent = Math.max(0, Math.min(1, clickX / rect.width));
    
    // 实时更新画面和进度条
    progressPercent.value = percent * 100;
    
    const newTime = percent * videoRef.value.duration;
    if (isFinite(newTime)) {
        videoRef.value.currentTime = newTime;
    }
};

const stopDrag = () => {
    isDragging.value = false;
    document.removeEventListener('mousemove', handleDrag);
    document.removeEventListener('mouseup', stopDrag);
};

const nextVideo = () => {
  if (currentIndex.value < videoList.value.length - 1) {
    transitionDirection.value = 'slide-up';
    currentIndex.value++;
  } else {
    ElMessage.info('没有更多视频了');
  }
};

const prevVideo = () => {
  if (currentIndex.value > 0) {
    transitionDirection.value = 'slide-down';
    currentIndex.value--;
  }
};

const handleWheel = (e) => {
    if (isScrolling.value) return;
    if (e.deltaY > 30) {
        nextVideo();
        lockScroll();
    } else if (e.deltaY < -30) {
        prevVideo();
        lockScroll();
    }
};

const lockScroll = () => {
    isScrolling.value = true;
    setTimeout(() => { isScrolling.value = false; }, 800);
};

const handleKeydown = (e) => {
    if (e.key === 'ArrowDown') nextVideo();
    if (e.key === 'ArrowUp') prevVideo();
    if (e.key === ' ') {
        e.preventDefault();
        togglePlay();
    }
};

const handleLike = async () => {
    if (!userStore.token) return ElMessage.warning('请先登录');
    const type = interaction.value.is_like ? 'unlike' : 'like';
    interaction.value.is_like = !interaction.value.is_like;
    if (interaction.value.is_like) currentVideo.value.likes++;
    else if (currentVideo.value.likes > 0) currentVideo.value.likes--;
    await postAction({ user_id: userStore.userInfo.id, video_id: currentVideo.value.id, type });
};

const togglePanel = (panelName) => { if (activePanel.value === panelName) { activePanel.value = 'none'; } else { activePanel.value = panelName; if (panelName === 'comments') loadComments(); } };
const loadComments = async () => { const res = await getComments(currentVideo.value.id, sortType.value, userStore.userInfo.id); commentsList.value = res.data.data.map(c => ({...c, expanded: false})); commentCount.value = res.data.data.length; };
const changeSort = (type) => { sortType.value = type; loadComments(); };

const postComment = async (parentId = null) => {
    if (!userStore.token) return ElMessage.warning('请先登录');
    const content = parentId ? replyText.value : commentText.value;
    if (!content) return;
    await sendComment({ user_id: userStore.userInfo.id, video_id: currentVideo.value.id, content: content, parent_id: parentId });
    commentText.value = ''; replyText.value = ''; replyTargetId.value = null; replyToUser.value = ''; // 清空回复状态
    loadComments();
};

const handleLikeComment = async (comment) => { if (!userStore.token) return ElMessage.warning('请先登录'); try { await likeComment(comment.id, userStore.userInfo.id); comment.likes++; } catch (e) {} };

// 【修改】打开回复框时，记录用户名但不放入输入框
const openReply = (cid, username) => { 
    replyTargetId.value = cid; 
    replyToUser.value = username; // 保存用户名用于 Tag 显示
    replyText.value = '';         // 输入框保持干净
};

const handlePin = async (cid) => { await pinComment({ user_id: userStore.userInfo.id, comment_id: cid }); loadComments(); };

const handleShare = () => { const url = window.location.href; navigator.clipboard.writeText(url).then(() => { ElMessage.success('链接已复制'); }); };
const formatCount = (num) => { if (!num) return 0; return num > 10000 ? (num/10000).toFixed(1) + '万' : num; }
const formatDate = (str) => {
   if (!str) return '';
   const date = new Date(str);
   return `${date.getFullYear()}年${date.getMonth()+1}月${date.getDate()}日`;
}

watch(() => currentIndex.value, playCurrent);

onMounted(() => { loadShorts(); window.addEventListener('keydown', handleKeydown); });
onBeforeUnmount(() => { window.removeEventListener('keydown', handleKeydown); });
</script>

<style scoped>
.shorts-container {
  width: 100%;
  height: calc(100vh - 56px); 
  display: flex; 
  justify-content: center;
  background: transparent; 
  overflow: hidden; 
  position: relative;
}

.shorts-viewport {
  width: 100%; 
  max-width: 1600px;
  height: 100%; 
  position: relative;
  display: flex; 
  align-items: center; 
  justify-content: center;
}

/* 核心布局: [左] [中] [右] [面板] */
.shorts-content-layout {
  display: flex; 
  align-items: flex-end; 
  justify-content: center;
  gap: 24px;
  height: 90%; 
  width: 100%; 
  position: relative;
}

/* 1. 左侧：信息栏 */
.left-side-info {
  width: 320px; 
  display: flex; flex-direction: column; 
  justify-content: flex-end; 
  align-items: flex-start; /* 左对齐 */
  text-align: left;
  height: 96%; 
  padding-bottom: 24px;
  gap: 12px; 
  z-index: 5;
}

.info-pill {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 30px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  display: flex; align-items: center; gap: 12px;
  transition: transform 0.2s;
  cursor: pointer;
  width: auto;
  max-width: 100%;
  margin-right: auto; 
  transform-origin: left center;
}
.info-pill:hover { transform: scale(1.02); background: #fff; }

.title-pill { max-width: 280px; }
.title-pill .pill-content { display: flex; align-items: center; gap: 8px; justify-content: space-between; width: 100%; }
.video-title { font-size: 14px; font-weight: 600; color: #0f0f0f; margin: 0; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.icon-right { color: #606060; }
.author-pill { justify-content: space-between; }
.author-row { display: flex; align-items: center; gap: 8px; }
.author-name { font-weight: bold; font-size: 14px; color: #0f0f0f; }
.yt-sub-btn { background: #0f0f0f; color: #fff; border: none; padding: 0 16px; height: 32px; border-radius: 16px; font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s; white-space: nowrap; flex-shrink: 0; }
.yt-sub-btn.subscribed { background: #f2f2f2; color: #0f0f0f; }

/* 2. 中间：播放器列 */
.center-column {
  width: 480px;
  aspect-ratio: 9 / 16;
  height: auto;
  max-height: 100%; 
  position: relative; 
  overflow: visible; 
  border-radius: 16px;
  
  box-shadow: 0 4px 24px rgba(0,0,0,0.15);
  flex-shrink: 0;
  z-index: 10;
}
.short-player-wrapper { width: 100%; height: 100%; position: absolute; top: 0; left: 0;  overflow: visible; will-change: transform; }
.short-video { width: 100%; height: 100%; object-fit: cover; border-radius: 16px; }

/* 3. 右侧：操作栏 */
.actions-side {
  width: 100px;
  display: flex; flex-direction: column; gap: 24px;
  justify-content: flex-end;
  height: 96%; padding-bottom: 40px;
  align-items: flex-start;
  flex-shrink: 0;
}
.action-btn { display: flex; flex-direction: column; align-items: center; gap: 6px; cursor: pointer; }
.icon-circle { 
  width: 48px; height: 48px; background: #f2f2f2; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #0f0f0f; transition: all 0.2s;
}
.icon-circle.active { background: #000; color: #fff; border-color: #000; } 
.action-label { color: #0f0f0f; font-size: 13px; font-weight: 500; }

/* 4. 扩展面板 */
.expand-panel {
  width: 360px; height: 96%; background: #fff; border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  display: flex; flex-direction: column; 
  overflow: hidden;
  margin-left: 20px; 
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.panel-header-row { display: flex; justify-content: space-between; align-items: center; padding: 15px; border-bottom: 1px solid #eee; background: #fff; flex-shrink: 0; }
.panel-title-switch { display: flex; align-items: center; gap: 10px; font-size: 16px; font-weight: bold; cursor: pointer; }
.panel-title-switch span:not(.active) { color: #909090; font-weight: normal; }
.panel-title-switch span.active { color: #0f0f0f; }
.panel-close { cursor: pointer; font-size: 20px; padding: 5px; }

/* 滚动区域 */
.panel-scroll-area { 
    overflow-y: auto; 
    flex: 1; 
    display: flex; 
    flex-direction: column;
}

.details-content { padding: 20px; }
.panel-video-title { font-size: 18px; font-weight: 600; margin-bottom: 20px; line-height: 1.4; }
.yt-stats-row { display: flex; justify-content: space-between; margin-top: 15px; padding: 0 10px; }
.s-item { text-align: center; width: 33%; }
.s-val { font-weight: bold; font-size: 16px; color: #0f0f0f; }
.s-lbl { font-size: 12px; color: #606060; margin-top: 4px; }
.detail-desc { font-size: 14px; line-height: 1.6; white-space: pre-wrap; color: #0f0f0f; margin-bottom: 15px; }
.hash-tag { color: #065fd4; margin-right: 5px; cursor: pointer; }

/* 评论区 */
.comments-content { display: flex; flex-direction: column; min-height: 100%; }
.comment-sort-bar { padding: 10px 15px; border-bottom: 1px solid #eee; font-size: 13px; font-weight: 500; display: flex; gap: 8px; flex-shrink: 0; }
.sort-chip { padding: 6px 12px; background: rgba(0,0,0,0.05); border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.2s; color: #0f0f0f; }
.sort-chip.active { background: #0f0f0f; color: white; }
.c-list { flex: 1; overflow-y: auto; padding: 15px; }
.c-user { font-size: 13px; font-weight: bold; color: #0f0f0f; margin-bottom: 4px; }
.c-time { font-size: 11px; color: #606060; margin-left: 5px; font-weight: normal; }
.c-text { font-size: 14px; color: #0f0f0f; line-height: 1.4; margin-bottom: 6px; }
.c-actions { display: flex; gap: 16px; font-size: 12px; color: #606060; cursor: pointer; align-items: center; }
.c-act-btn { display: flex; align-items: center; gap: 4px; }
.c-act-btn.liked { color: #065fd4; }
.more-icon { transform: rotate(90deg); cursor: pointer; }
.pinned-badge { font-size: 12px; color: #fff; background: #606060; display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 2px; margin-bottom: 8px; font-weight: 500; }

/* 回复框样式优化 */
.reply-box { margin-top: 10px; padding: 10px; background: #f9f9f9; border-radius: 8px; border: 1px solid #eee; }
.reply-target-tag { margin-bottom: 6px; font-size: 12px; color: #065fd4; font-weight: 500; background: rgba(6, 95, 212, 0.1); display: inline-block; padding: 2px 8px; border-radius: 4px; }
.reply-acts { text-align: right; margin-top: 5px; }
.reply-toggle { font-size: 12px; color: #065fd4; cursor: pointer; margin-top: 5px; display: flex; align-items: center; gap: 4px; }
.sub-item { margin-top: 10px; }

/* 底部 Footer */
.panel-footer { 
    padding: 15px; 
    border-top: 1px solid #eee; 
    background: #fff; 
    flex-shrink: 0; 
    z-index: 10;
}

/* 导航按钮 */
.nav-btn { 
  position: absolute; 
  right: 48px; 
  top: 50%;    
  width: 48px; height: 48px; 
  background: rgba(0,0,0,0.05); 
  border-radius: 50%; 
  display: flex; align-items: center; justify-content: center; 
  cursor: pointer; color: #333; z-index: 10; 
  transition: all 0.2s; 
  transform: translateY(-50%);
}
.nav-btn:hover { background: rgba(0,0,0,0.1); transform: translateY(-50%) scale(1.1); }
.nav-btn.prev { top: calc(50% - 60px); }
.nav-btn.next { top: calc(50% + 60px); }

.play-mask { position: absolute; top:0; left:0; right:0; bottom:0; display:flex; align-items:center; justify-content:center; background: rgba(0,0,0,0.2); border-radius: 16px; }
.play-icon-bg { background: rgba(0,0,0,0.6); border-radius: 50%; padding: 15px; display: flex; color: white; }

/* ============ 进度条样式 (可拖动增强) ============ */
.progress-bar-container { 
    position: absolute; 
    bottom: 0; left: 12px; right: 12px; 
    height: 15px; /* 增加感应区域高度 */
    background: transparent; 
    z-index: 2; 
    cursor: pointer; /* 鼠标变手型 */
    display: flex;
    align-items: flex-end; /* 进度条靠底 */
}
.progress-bar-container:hover .progress-bar { height: 5px; }
.progress-bar-container:hover .progress-thumb { transform: scale(1); }

/* 背景槽 */
.progress-bg { position: absolute; bottom: 0; left: 0; width: 100%; height: 3px; background: rgba(255,255,255,0.3); border-radius: 2px; }

/* 实际进度 */
.progress-bar { 
    position: absolute; bottom: 0; left: 0;
    height: 3px; 
    background: #ff0000; 
    transition: width 0.1s linear, height 0.1s; 
    pointer-events: none; /* 让点击穿透到 container */
    border-radius: 2px;
}

/* 拖动滑块(圆点) */
.progress-thumb {
    position: absolute;
    bottom: -3px; /* 微调位置居中 */
    width: 12px; height: 12px;
    background: #ff0000;
    border-radius: 50%;
    transform: scale(0); /* 默认隐藏 */
    transition: transform 0.1s;
    margin-left: -6px; /* 居中校正 */
    pointer-events: none;
}

/* 动画通用设置 */
.slide-up-enter-active, .slide-up-leave-active,
.slide-down-enter-active, .slide-down-leave-active,
.slide-panel-enter-active, .slide-panel-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.44, 0.94);
}
.slide-up-enter-from { transform: translateY(100%); }
.slide-up-enter-to { transform: translateY(0); }
.slide-up-leave-from { transform: translateY(0); }
.slide-up-leave-to { transform: translateY(-100%); }
.slide-down-enter-from { transform: translateY(-100%); }
.slide-down-enter-to { transform: translateY(0); }
.slide-down-leave-from { transform: translateY(0); }
.slide-down-leave-to { transform: translateY(100%); }
.slide-panel-enter-from, .slide-panel-leave-to { width: 0; opacity: 0; margin-left: 0; }
</style>