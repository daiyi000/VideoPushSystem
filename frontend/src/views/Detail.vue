<template>
  <div class="detail-container">
    <div v-if="video" class="main-layout">
      
      <el-row :gutter="24">
        <!-- 左侧：播放器 + 信息 + 评论 -->
        <el-col :span="17" :xs="24">
          <div class="content-wrapper">
            <!-- 播放器容器 -->
            <div class="video-container">
              <video 
                ref="videoRef" :src="video.url" controls autoplay class="real-video"
                @timeupdate="handleTimeUpdate" @play="onVideoPlay" @pause="onVideoPause">
              </video>
              <div class="danmaku-layer" :style="{ animationPlayState: isVideoPaused ? 'paused' : 'running' }">
                <div v-for="dm in activeDanmakus" :key="dm.id" class="danmaku-item"
                  :style="{ top: dm.top + '%', color: dm.color, animationDuration: dm.speed + 's', animationPlayState: isVideoPaused ? 'paused' : 'running' }">
                  {{ dm.text }}
                </div>
              </div>
              <div class="danmaku-input-bar">
                <el-color-picker v-model="danmakuColor" size="small" show-alpha />
                <input v-model="danmakuText" class="dm-input" placeholder="发个弹幕..." @keyup.enter="fireDanmaku"/>
                <button class="dm-send-btn" @click="fireDanmaku">发送</button>
              </div>
            </div>
            
            <!-- 视频信息区 -->
            <div class="info-section">
              <h1 class="title">{{ video.title }}</h1>
              
              <div class="action-bar">
                <div class="left-meta">
                  <div class="uploader-mini" @click="$router.push(`/channel/${video.uploader_id}`)">
                    <el-avatar :size="40" :src="video.uploader_avatar" />
                    <div class="uploader-text">
                      <div class="name">{{ video.uploader_name }}</div>
                      <div class="subs">{{ channelStats.fans }} 位订阅者</div>
                    </div>
                  </div>
                  <button 
                    class="yt-sub-btn" 
                    :class="{ subscribed: channelStats.is_following }"
                    @click="handleSubscribe"
                  >
                    {{ channelStats.is_following ? '已订阅' : '订阅' }}
                  </button>
                </div>
                
                <div class="right-actions">
                  <div class="yt-like-btn" @click="toggleLike" :class="{ active: interaction.is_like }">
                    <el-icon size="20">
                      <svg v-if="interaction.is_like" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-1.91l-.01-.01L23 10z"/></svg>
                      <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M9 21h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.58 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2zM9 9l4.34-4.34L12 10h9v2l-3 7H9V9zM1 9h4v12H1z"/></svg>
                    </el-icon>
                    <span class="like-count">{{ formatCount(currentLikes) }}</span>
                  </div>
                  <div class="yt-action-btn" @click="toggleFav" :class="{ active: interaction.is_fav }">
                    <el-icon size="20" v-if="interaction.is_fav"><StarFilled style="fill: #e6a23c" /></el-icon>
                    <el-icon size="20" v-else><Star /></el-icon>
                    <span>{{ interaction.is_fav ? '已收藏' : '收藏' }}</span>
                  </div>
                </div>
              </div>
              
              <div class="description-box">
                <div class="desc-meta"><span>{{ video.views }}次观看</span> • <span>{{ formatTime(video.upload_time) }}</span></div>
                <div class="desc-text">{{ video.description || '暂无简介' }}</div>
              </div>
            </div>

            <!-- 评论区 -->
            <div class="comment-section">
              <div class="comment-header">
                <h3>{{ comments.length }} 条评论</h3>
                <div class="sort-btn" @click="toggleSort">
                  <el-icon><Sort /></el-icon> 
                  <span>排序方式：{{ sortType === 'hot' ? '最热优先' : '最新优先' }}</span>
                </div>
              </div>
              <div class="comment-input">
                <el-avatar :size="40" :src="userStore.userInfo.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'" />
                <div class="input-wrapper">
                  <el-input v-model="commentText" type="textarea" :rows="1" placeholder="添加评论..." class="yt-input" />
                  <div class="input-actions" v-if="commentText">
                    <el-button round size="small" @click="commentText = ''">取消</el-button>
                    <el-button type="primary" round size="small" @click="postComment(null)">评论</el-button>
                  </div>
                </div>
              </div>
              <div class="comment-list">
                <div v-for="c in comments" :key="c.id" class="comment-item">
                  <el-avatar :size="40" :src="c.user.avatar" class="c-avatar" />
                  <div class="c-body">
                    <div v-if="c.is_pinned" class="pinned-badge">
                      <el-icon><Top /></el-icon> 由 {{ video.uploader_name }} 置顶
                    </div>
                    <div class="c-header"><span class="c-user">@{{ c.user.username }}</span><span class="c-time">{{ c.time }}</span></div>
                    <div class="c-text">{{ c.content }}</div>
                    <div class="c-actions">
                      <div class="c-action-btn" @click="handleLikeComment(c)" :class="{ 'is-liked': c.is_liked }">
                        <svg v-if="c.is_liked" style="width:16px;height:16px;margin-right:4px;" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-1.91l-.01-.01L23 10z"/></svg>
                        <svg v-else style="width:16px;height:16px;margin-right:4px;" viewBox="0 0 24 24" fill="currentColor"><path d="M9 21h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.58 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2zM9 9l4.34-4.34L12 10h9v2l-3 7H9V9zM1 9h4v12H1z"/></svg>
                        {{ c.likes || '' }}
                      </div>
                      <div class="c-action-btn" @click="openReply(c.id, c.user.username)">回复</div>
                      <el-dropdown v-if="isOwner" trigger="click" @command="handlePin(c.id)">
                        <span class="c-more-btn"><el-icon><MoreFilled /></el-icon></span>
                        <template #dropdown><el-dropdown-menu><el-dropdown-item>{{ c.is_pinned ? '取消置顶' : '置顶评论' }}</el-dropdown-item></el-dropdown-menu></template>
                      </el-dropdown>
                    </div>
                    <div v-if="replyTargetId === c.id" class="reply-input-box">
                      <el-input v-model="replyText" size="small" placeholder="写下你的回复..." />
                      <div class="reply-btns"><el-button size="small" @click="replyTargetId = null">取消</el-button><el-button type="primary" size="small" @click="postComment(c.id)">回复</el-button></div>
                    </div>
                    <div v-if="c.replies && c.replies.length > 0">
                      <div class="replies-toggle" v-if="!c.expanded" @click="c.expanded = true"><el-icon><CaretBottom /></el-icon> 展开 {{ c.replies.length }} 条回复</div>
                      <div v-else>
                        <div v-for="r in c.replies" :key="r.id" class="reply-item">
                          <el-avatar :size="24" :src="r.user.avatar" class="r-avatar" />
                          <div class="r-body"><div class="c-header"><span class="c-user">@{{ r.user.username }}</span><span class="c-time">{{ r.time }}</span></div><div class="c-text">{{ r.content }}</div>
                            <div class="c-actions"><div class="c-action-btn" @click="handleLikeComment(r)" :class="{ 'is-liked': r.is_liked }"><svg v-if="r.is_liked" style="width:14px;height:14px;margin-right:4px;" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-1.91l-.01-.01L23 10z"/></svg><svg v-else style="width:14px;height:14px;margin-right:4px;" viewBox="0 0 24 24" fill="currentColor"><path d="M9 21h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.58 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2zM9 9l4.34-4.34L12 10h9v2l-3 7H9V9zM1 9h4v12H1z"/></svg>{{ r.likes || '' }}</div><div class="c-action-btn" @click="openReply(c.id, r.user.username)">回复</div></div>
                          </div>
                        </div>
                        <div class="replies-toggle" @click="c.expanded = false"><el-icon><CaretTop /></el-icon> 收起</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 右侧：推荐列表 -->
        <el-col :span="7" :xs="24">
          <div class="sidebar-content">
            
            <!-- 【新增】播放列表卡片 (仅当 URL 带 list 参数时显示) -->
            <div v-if="playlistVideos.length > 0" class="playlist-panel">
              <div class="panel-header">
                <div class="panel-title">正在播放</div>
                <div class="panel-subtitle">当前播放列表</div>
              </div>
              <div class="panel-list">
                <div 
                  v-for="(v, index) in playlistVideos" 
                  :key="v.id" 
                  class="panel-item" 
                  :class="{ active: String(v.id) === String(video.id) }"
                  @click="goToVideo(v.id, route.query.list)"
                >
                  <div class="panel-index" v-if="String(v.id) !== String(video.id)">{{ index + 1 }}</div>
                  <div class="panel-index" v-else><el-icon><VideoPlay /></el-icon></div>
                  
                  <div class="panel-thumb">
                    <img :src="v.cover_url">
                  </div>
                  <div class="panel-info">
                    <div class="panel-v-title">{{ v.title }}</div>
                    <div class="panel-v-author">{{ v.uploader_name }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 相关视频推荐 (排在播放列表下方) -->
            <div class="recommend-list">
              <div v-for="item in relatedVideos" :key="item.id" class="related-item" @click="goToVideo(item.id)">
                <div class="related-cover-box"><img :src="item.cover_url" class="related-cover"/><span class="duration">10:24</span></div>
                <div class="related-info"><div class="related-title">{{ item.title }}</div><div class="related-meta">{{ item.uploader_name }}</div><div class="related-meta">{{ item.views }}次观看</div></div>
              </div>
            </div>
            
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
import { getVideoDetail, postAction, checkFavStatus } from '../api/video';
import { getRelatedVideos } from '../api/recommend';
import { getComments, sendComment, likeComment, pinComment, getDanmaku, sendDanmaku, checkInteractionStatus } from '../api/interaction';
import { toggleFollow, getChannelInfo } from '../api/user';
import { getPlaylistVideos } from '../api/playlist'; // 引入 API
import { ElMessage } from 'element-plus';
import { Star, StarFilled, Sort, CaretBottom, CaretTop, MoreFilled, Top, VideoPlay } from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const videoRef = ref(null);

const video = ref(null);
const relatedVideos = ref([]);
const currentLikes = ref(0);
const interaction = ref({ is_fav: false, is_like: false });
const channelStats = ref({ fans: 0, is_following: false });

const comments = ref([]);
const commentText = ref('');
const replyText = ref('');
const replyTargetId = ref(null);
const sortType = ref('hot');

const danmakuText = ref('');
const danmakuColor = ref('#FFFFFF');
const allDanmakus = ref([]); 
const activeDanmakus = ref([]);
const isVideoPaused = ref(false);

// 播放列表数据
const playlistVideos = ref([]);

const isOwner = computed(() => {
  if (!video.value || !userStore.userInfo) return false;
  return String(video.value.uploader_id) === String(userStore.userInfo.id);
});

const loadPageData = async (videoId) => {
  activeDanmakus.value = [];
  try {
    const res = await getVideoDetail(videoId);
    video.value = res.data.data;
    currentLikes.value = res.data.data.likes || 0;
    
    const channelRes = await getChannelInfo({
      author_id: video.value.uploader_id,
      visitor_id: userStore.token ? userStore.userInfo.id : null
    });
    channelStats.value = channelRes.data.data.stats;

    // 1. 加载相关推荐
    const recRes = await getRelatedVideos(videoId);
    relatedVideos.value = recRes.data.data;

    // 2. 检查是否有 playlist 参数，如果有，加载播放列表
    if (route.query.list) {
      const plRes = await getPlaylistVideos(route.query.list);
      if (plRes.data.code === 200) {
        playlistVideos.value = plRes.data.data;
      }
    } else {
      playlistVideos.value = []; // 清空防止残留
    }

    loadComments();
    loadDanmaku(videoId);

    if (userStore.token) {
      const statusRes = await checkInteractionStatus(userStore.userInfo.id, videoId);
      interaction.value = statusRes.data.data;
      postAction({ user_id: userStore.userInfo.id, video_id: videoId, type: 'view' });
    }
  } catch (e) {
    console.error(e);
    if (e.response && (e.response.status === 404 || e.response.status === 403)) {
      router.replace('/404');
    }
  }
};

// 统一跳转方法
const goToVideo = (vid, playlistId = null) => {
  if (playlistId) {
    router.push({ path: `/video/${vid}`, query: { list: playlistId } });
  } else {
    // 如果之前有 list 参数，点击普通推荐时移除 list 参数
    router.push({ path: `/video/${vid}` });
  }
};

const handleSubscribe = async () => {
  if (!userStore.token) return ElMessage.warning('请先登录');
  if (String(userStore.userInfo.id) === String(video.value.uploader_id)) return ElMessage.warning('不能订阅自己');
  try {
    const res = await toggleFollow({ follower_id: userStore.userInfo.id, followed_id: video.value.uploader_id });
    if (res.data.code === 200) {
      channelStats.value.is_following = res.data.is_following;
      channelStats.value.fans = res.data.fans_count;
      ElMessage.success(res.data.is_following ? '订阅成功' : '已取消订阅');
    }
  } catch (e) { ElMessage.error('操作失败'); }
};

const onVideoPause = () => { isVideoPaused.value = true; };
const onVideoPlay = () => { isVideoPaused.value = false; };
const loadComments = async () => { const uid = userStore.token ? userStore.userInfo.id : null; const res = await getComments(video.value.id, sortType.value, uid); comments.value = res.data.data.map(c => ({ ...c, expanded: false })); };
const toggleSort = () => { sortType.value = sortType.value === 'hot' ? 'new' : 'hot'; loadComments(); };
const postComment = async (parentId = null) => { if (!userStore.token) return ElMessage.warning('请先登录'); const content = parentId ? replyText.value : commentText.value; if (!content.trim()) return; await sendComment({ user_id: userStore.userInfo.id, video_id: video.value.id, content: content, parent_id: parentId }); commentText.value = ''; replyText.value = ''; replyTargetId.value = null; ElMessage.success('评论成功'); loadComments(); };
const openReply = (rootId, targetUsername = null) => { if (!userStore.token) return ElMessage.warning('请先登录'); replyTargetId.value = rootId; if (targetUsername) { replyText.value = `回复 @${targetUsername} : `; } else { replyText.value = ''; } };
const handleLikeComment = async (comment) => { if (!userStore.token) return ElMessage.warning('请先登录'); try { const res = await likeComment(comment.id, userStore.userInfo.id); if (res.data.code === 200) { comment.likes = res.data.likes; comment.is_liked = (res.data.action === 'like'); } } catch (e) { console.error(e); } };
const handlePin = async (commentId) => { try { await pinComment({ user_id: userStore.userInfo.id, comment_id: commentId }); ElMessage.success('操作成功'); loadComments(); } catch (e) { ElMessage.error('操作失败'); } };
const toggleLike = async () => { if (!userStore.token) return ElMessage.warning('请先登录'); const isLiking = !interaction.value.is_like; const type = isLiking ? 'like' : 'unlike'; try { interaction.value.is_like = isLiking; if (isLiking) { currentLikes.value += 1; } else { currentLikes.value -= 1; } await postAction({ user_id: userStore.userInfo.id, video_id: video.value.id, type }); } catch (e) { interaction.value.is_like = !isLiking; currentLikes.value = isLiking ? currentLikes.value - 1 : currentLikes.value + 1; ElMessage.error('操作失败'); } };
const toggleFav = async () => { if (!userStore.token) return ElMessage.warning('请先登录'); const type = interaction.value.is_fav ? 'unfavorite' : 'favorite'; try { await postAction({ user_id: userStore.userInfo.id, video_id: video.value.id, type }); interaction.value.is_fav = !interaction.value.is_fav; } catch (e) { ElMessage.error('操作失败'); } };
const loadDanmaku = async (vid) => { const res = await getDanmaku(vid); allDanmakus.value = res.data.data; };
const fireDanmaku = async () => { if (!userStore.token) return ElMessage.warning('登录后发弹幕'); if (!danmakuText.value) return; const time = videoRef.value.currentTime; const text = danmakuText.value; const color = danmakuColor.value || '#FFFFFF'; await sendDanmaku({ user_id: userStore.userInfo.id, video_id: video.value.id, text, time, color }); pushDanmakuToScreen({ text, color }); danmakuText.value = ''; ElMessage.success('发射成功'); };
const pushDanmakuToScreen = (dm) => { const id = Date.now() + Math.random(); activeDanmakus.value.push({ id, text: dm.text, color: dm.color, top: Math.random() * 80, speed: 5 + Math.random() * 5 }); setTimeout(() => { activeDanmakus.value = activeDanmakus.value.filter(d => d.id !== id); }, 10000); };
const handleTimeUpdate = (e) => { const currentTime = e.target.currentTime; allDanmakus.value.forEach(dm => { if (Math.abs(dm.time - currentTime) < 0.5 && !dm.shown) { pushDanmakuToScreen(dm); dm.shown = true; } }); };
const formatCount = (num) => num >= 10000 ? (num / 10000).toFixed(1) + '万' : num;
const formatTime = (timeStr) => timeStr ? timeStr.split(' ')[0] : '';

watch(() => route.params.id, (newId) => { if(newId) loadPageData(newId); });
onMounted(() => { if(route.params.id) loadPageData(route.params.id); });
</script>

<style scoped>
.content-wrapper { background: transparent; margin-bottom: 20px; }
.video-container { position: relative; width: 100%; aspect-ratio: 16/9; background: #000; overflow: hidden; border-radius: 12px; }
.real-video { width: 100%; height: 100%; }
.danmaku-layer { position: absolute; top: 0; left: 0; width: 100%; height: 85%; pointer-events: none; overflow: hidden; }
.danmaku-item { position: absolute; right: -100px; white-space: nowrap; font-size: 20px; font-weight: bold; text-shadow: 1px 1px 2px black; animation-name: danmaku-move; animation-timing-function: linear; will-change: transform, left; }
@keyframes danmaku-move { from { transform: translateX(0); left: 100%; } to { transform: translateX(-200%); left: -100%; } }
.danmaku-input-bar { position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%); display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.6); padding: 5px 15px; border-radius: 30px; opacity: 0; transition: opacity 0.3s; z-index: 10;}
.video-container:hover .danmaku-input-bar { opacity: 1; }
.dm-input { background: transparent; border: none; color: white; width: 200px; outline: none; font-size: 14px; }
.dm-send-btn { background: #409EFF; border: none; color: white; border-radius: 15px; padding: 5px 15px; cursor: pointer; font-size: 12px; }

.info-section { padding: 20px 0; }
.title { font-size: 20px; font-weight: 700; margin: 0 0 10px 0; line-height: 28px; color: #0f0f0f; }
.action-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px; }
.left-meta { display: flex; align-items: center; gap: 20px; }
.uploader-mini { display: flex; align-items: center; gap: 12px; cursor: pointer; }
.uploader-text .name { font-weight: 600; font-size: 16px; color: #0f0f0f; }
.uploader-text .subs { font-size: 12px; color: #606060; }
.yt-sub-btn { background: #0f0f0f; color: #fff; border: none; padding: 0 16px; height: 36px; border-radius: 18px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; }
.yt-sub-btn:hover { background: #272727; }
.yt-sub-btn.subscribed { background: #f2f2f2; color: #0f0f0f; }
.yt-sub-btn.subscribed:hover { background: #e5e5e5; }

.right-actions { display: flex; gap: 10px; }
.yt-like-btn, .yt-action-btn { display: flex; align-items: center; height: 36px; border-radius: 18px; background-color: #f2f2f2; padding: 0 16px; cursor: pointer; font-size: 14px; font-weight: 500; color: #0f0f0f; gap: 8px; user-select: none; }
.yt-like-btn:hover, .yt-action-btn:hover { background-color: #e5e5e5; }
.yt-like-btn.active, .yt-action-btn.active { background-color: #0f0f0f; color: #fff; }
.description-box { background-color: #f2f2f2; border-radius: 12px; padding: 12px; margin-top: 10px; font-size: 14px; cursor: pointer; }
.desc-meta { font-weight: 600; color: #0f0f0f; margin-bottom: 8px; }
.desc-text { color: #0f0f0f; line-height: 20px; white-space: pre-wrap; }

.comment-section { margin-top: 24px; }
.comment-header { display: flex; align-items: center; gap: 30px; margin-bottom: 24px; }
.sort-btn { display: flex; align-items: center; gap: 8px; font-weight: 500; cursor: pointer; font-size: 14px; color: #0f0f0f; }
.comment-input { display: flex; gap: 16px; margin-bottom: 32px; }
.input-wrapper { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.input-actions { display: flex; justify-content: flex-end; gap: 8px; }
.comment-item { display: flex; gap: 16px; margin-bottom: 24px; }
.c-body { flex: 1; }
.pinned-badge { font-size: 12px; color: #fff; background: #606060; display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 2px; margin-bottom: 8px; font-weight: 500; }
.c-header { margin-bottom: 4px; font-size: 13px; }
.c-user { font-weight: 600; color: #0f0f0f; margin-right: 5px; }
.c-time { color: #606060; }
.c-text { font-size: 14px; line-height: 20px; color: #0f0f0f; margin-bottom: 8px; }
.c-actions { display: flex; gap: 16px; align-items: center; color: #606060; font-size: 12px; user-select: none; }
.c-action-btn { cursor: pointer; display: flex; align-items: center; gap: 4px; }
.c-action-btn:hover { color: #0f0f0f; }
.c-action-btn.is-liked { color: #065fd4; }
.c-more-btn { transform: rotate(90deg); cursor: pointer; display: none; }
.comment-item:hover .c-more-btn { display: inline-block; }
.reply-input-box { margin-top: 10px; margin-bottom: 10px; }
.reply-btns { margin-top: 8px; display: flex; justify-content: flex-end; gap: 10px; }
.replies-toggle { margin-top: 8px; color: #065fd4; font-size: 14px; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 5px; width: fit-content; border-radius: 18px; padding: 5px 10px; }
.replies-toggle:hover { background-color: #def1ff; }
.reply-item { display: flex; gap: 10px; margin-top: 10px; margin-bottom: 10px; }

/* 侧边栏整体容器 */
.sidebar-content { display: flex; flex-direction: column; gap: 20px; }

/* 播放列表面板样式 */
.playlist-panel {
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
}
.panel-header {
  background: #f2f2f2;
  padding: 15px;
  border-bottom: 1px solid #e5e5e5;
}
.panel-title { font-weight: bold; font-size: 16px; margin-bottom: 4px; }
.panel-subtitle { font-size: 12px; color: #606060; }

.panel-list {
  max-height: 400px;
  overflow-y: auto;
}
.panel-item {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  cursor: pointer;
  transition: background 0.2s;
}
.panel-item:hover { background: #f2f2f2; }
.panel-item.active { background: #e5e5e5; }

.panel-index { width: 24px; font-size: 12px; color: #606060; text-align: center; }
.panel-thumb { width: 100px; height: 56px; border-radius: 4px; overflow: hidden; margin: 0 10px; flex-shrink: 0; }
.panel-thumb img { width: 100%; height: 100%; object-fit: cover; }
.panel-info { flex: 1; min-width: 0; }
.panel-v-title { font-size: 14px; font-weight: 600; color: #0f0f0f; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.panel-v-author { font-size: 12px; color: #606060; }

/* 推荐视频列表 */
.recommend-list { display: flex; flex-direction: column; gap: 8px; }
.related-item { display: flex; gap: 8px; cursor: pointer; }
.related-cover-box { position: relative; width: 168px; height: 94px; border-radius: 8px; overflow: hidden; flex-shrink: 0; background: #ddd; }
.related-cover { width: 100%; height: 100%; object-fit: cover; }
.duration { position: absolute; bottom: 4px; right: 4px; background: rgba(0,0,0,0.8); color: white; font-size: 12px; padding: 1px 4px; border-radius: 4px; font-weight: 500; }
.related-info { display: flex; flex-direction: column; gap: 4px; }
.related-title { font-size: 14px; font-weight: 600; color: #0f0f0f; line-height: 20px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.related-meta { font-size: 12px; color: #606060; }
</style>