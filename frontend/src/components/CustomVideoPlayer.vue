<template>
  <div 
    class="custom-player" 
    ref="playerContainer"
    @mousemove="handleMouseMove"
    @mouseleave="showControls = false"
    :class="{ 'hide-cursor': !showControls && isPlaying }"
  >
    <video 
      ref="videoRef"
      :src="src" 
      class="video-element"
      @click="togglePlay"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @progress="onProgress"
      @ended="onEnded"
    >
       <!-- Add subtitle track if provided -->
       <track v-if="subtitleUrl" :src="subtitleUrl" kind="subtitles" srclang="zh" label="Chinese" default />
    </video>

    <!-- 遮罩层：暂停时显示大图标 -->
    <div class="center-overlay" v-if="!isPlaying && !isEnded" @click="togglePlay">
       <div class="play-icon-bg">
         <el-icon size="40" color="#fff"><VideoPlay /></el-icon>
       </div>
    </div>

    <!-- 【手动片尾】End Screen Overlay (Playing) -->
    <div class="end-screen-overlay" v-if="showEndScreenOverlay">
      <div class="end-screen-content">
        <div class="end-grid">
           <div 
             v-for="item in endScreenOverlayList" 
             :key="item.id" 
             class="end-card"
             @click.stop="playNext(item.id)"
           >
              <div class="end-card-img">
                 <img :src="item.cover_url" />
                 <span class="end-duration">{{ formatDuration(item.duration) }}</span>
              </div>
              <div class="end-card-info">
                 <div class="end-title">{{ item.title }}</div>
                 <div class="end-author">{{ item.uploader_name }}</div>
              </div>
           </div>
        </div>
      </div>
    </div>

    <!-- 【自动推荐】Post Roll (Ended) -->
    <div class="post-roll-overlay" v-if="showPostRoll">
       <div class="post-roll-header">接下来播放</div>
       <div class="post-roll-grid">
          <div 
             v-for="item in postRollList" 
             :key="item.id" 
             class="post-card"
             @click.stop="playNext(item.id)"
           >
              <div class="post-thumb">
                 <img :src="item.cover_url" />
                 <span class="post-duration">{{ formatDuration(item.duration) }}</span>
              </div>
              <div class="post-info">
                 <div class="post-title">{{ item.title }}</div>
                 <div class="post-author">{{ item.uploader_name }}</div>
              </div>
           </div>
       </div>
       <div class="post-replay-btn" @click.stop="togglePlay">
          <el-icon><RefreshRight /></el-icon> 重播
       </div>
    </div>

    <!-- 底部控制栏 -->
    <div class="controls-bar" :class="{ 'visible': showControls || !isPlaying }">
      <!-- 进度条 -->
      <div class="progress-container" 
       ref="progressRef"
       @mousedown="startDrag" 
       @click="seek"> <div class="progress-bg"></div>
    <div class="progress-buffered" :style="{ width: bufferedPercentage + '%' }"></div>
    <div class="progress-current" :style="{ width: currentPercentage + '%' }">
      <div class="progress-handle"></div>
    </div>
  </div>

      <div class="controls-row">
        <div class="left-controls">
          <el-icon class="ctrl-btn" @click="togglePlay" size="24">
            <VideoPause v-if="isPlaying" />
            <VideoPlay v-else />
          </el-icon>
          
          <div class="volume-box">
             <el-icon class="ctrl-btn" @click="toggleMute" size="24">
               <Mute v-if="isMuted || volume === 0" />
               <Microphone v-else /> 
             </el-icon>
             <input type="range" min="0" max="1" step="0.1" v-model="volume" class="volume-slider" @input="updateVolume">
          </div>

          <div class="time-display">
            {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
          </div>
        </div>

        <div class="right-controls">
          <!-- CC Button -->
          <el-icon v-if="subtitleUrl" class="ctrl-btn" @click="toggleSubtitle" size="24" :color="showSubtitle ? '#fff' : '#909090'">
            <ChatLineSquare />
          </el-icon>
          <el-icon class="ctrl-btn" @click="toggleFullscreen" size="24"><FullScreen /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue';
import { VideoPlay, VideoPause, FullScreen, Microphone, Mute, ChatLineSquare, RefreshRight } from '@element-plus/icons-vue';

const props = defineProps({
  src: String,
  autoplay: { type: Boolean, default: false },
  endScreenData: { type: Array, default: () => [] }, // 手动片尾 (Overlay)
  postRollData: { type: Array, default: () => [] }, // 自动推荐 (Post-roll)
  subtitleUrl: { type: String, default: '' }
});

const emit = defineEmits(['timeupdate', 'play', 'pause', 'ended', 'navigate']);

const videoRef = ref(null);
const playerContainer = ref(null);

const isPlaying = ref(false);
const isEnded = ref(false); // New state
const currentTime = ref(0);
const duration = ref(0);
const currentPercentage = ref(0);
const bufferedPercentage = ref(0);
const volume = ref(1);
const isMuted = ref(false);
const showControls = ref(true);
let controlTimer = null;
const isDragging = ref(false); 
const progressRef = ref(null); 

const showSubtitle = ref(true);

// 1. Manual End Screen Overlay (Last 10s)
const showEndScreenOverlay = computed(() => {
  if (!duration.value) return false;
  if (isEnded.value) return false; // Hide overlay when video ends, show Post Roll instead
  const isNearEnd = (duration.value - currentTime.value) <= 10;
  return (isNearEnd && props.endScreenData.length > 0);
});

// 2. Post Roll Screen (When Ended)
const showPostRoll = computed(() => {
  return isEnded.value && (props.postRollData.length > 0 || props.endScreenData.length > 0);
});

const endScreenOverlayList = computed(() => {
  return props.endScreenData.slice(0, 2); 
});

const postRollList = computed(() => {
  // Combine manual and auto if needed, or just use auto
  // Let's use postRollData (which is relatedVideos from Detail.vue)
  return props.postRollData.slice(0, 12); 
});

const formatDuration = (s) => {
    if(!s) return '0:00';
    const m = Math.floor(s/60);
    const sec = Math.floor(s%60);
    return `${m}:${sec.toString().padStart(2,'0')}`;
}

const playNext = (id) => {
    emit('navigate', id);
    isEnded.value = false; // Reset ended state
};

const toggleSubtitle = () => {
    showSubtitle.value = !showSubtitle.value;
    if (videoRef.value && videoRef.value.textTracks && videoRef.value.textTracks[0]) {
        videoRef.value.textTracks[0].mode = showSubtitle.value ? 'showing' : 'hidden';
    }
};

const formatTime = (time) => {
  if (!time || isNaN(time)) return '0:00';
  const m = Math.floor(time / 60);
  const s = Math.floor(time % 60);
  return `${m}:${s < 10 ? '0' + s : s}`;
};

const togglePlay = () => {
  if (isEnded.value) {
      // Replay
      videoRef.value.currentTime = 0;
      isEnded.value = false;
      videoRef.value.play();
      isPlaying.value = true;
      emit('play');
      return;
  }

  if (videoRef.value.paused) {
    videoRef.value.play();
    isPlaying.value = true;
    emit('play');
  } else {
    videoRef.value.pause();
    isPlaying.value = false;
    emit('pause');
  }
};

const onTimeUpdate = () => {
  if (isDragging.value) return; 
  currentTime.value = videoRef.value.currentTime;
  currentPercentage.value = (currentTime.value / duration.value) * 100;
  emit('timeupdate', videoRef.value.currentTime);
};

const startDrag = (e) => {
  isDragging.value = true;
  handleDrag(e); 
  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('mouseup', stopDrag);
};

const handleDrag = (e) => {
  if (!duration.value) return;
  const rect = progressRef.value.getBoundingClientRect();
  let pos = (e.clientX - rect.left) / rect.width;
  pos = Math.max(0, Math.min(1, pos));
  currentPercentage.value = pos * 100;
  videoRef.value.currentTime = pos * duration.value;
  if(isEnded.value) isEnded.value = false;
};

const stopDrag = (e) => {
  if (isDragging.value) {
    handleDrag(e);
    isDragging.value = false;
    document.removeEventListener('mousemove', handleDrag);
    document.removeEventListener('mouseup', stopDrag);
  }
};

const onLoadedMetadata = () => {
  duration.value = videoRef.value.duration;
  isEnded.value = false;
  if (props.autoplay) togglePlay();
  
  if (videoRef.value.textTracks && videoRef.value.textTracks[0]) {
       videoRef.value.textTracks[0].mode = showSubtitle.value ? 'showing' : 'hidden';
  }
};

const onProgress = () => {
  if (videoRef.value.buffered.length > 0) {
    const bufferedEnd = videoRef.value.buffered.end(videoRef.value.buffered.length - 1);
    bufferedPercentage.value = (bufferedEnd / duration.value) * 100;
  }
};

const onEnded = () => {
  isPlaying.value = false;
  isEnded.value = true;
  emit('ended');
};

const seek = (e) => {
  if(!isDragging.value) {
     const rect = progressRef.value.getBoundingClientRect();
     const pos = (e.clientX - rect.left) / rect.width;
     videoRef.value.currentTime = pos * duration.value;
     if(isEnded.value) isEnded.value = false;
  }
};

const updateVolume = () => { videoRef.value.volume = volume.value; isMuted.value = volume.value === 0; };
const toggleMute = () => {
  if (isMuted.value) {
    videoRef.value.volume = volume.value || 1;
    isMuted.value = false;
  } else {
    videoRef.value.volume = 0;
    isMuted.value = true;
  }
};

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    playerContainer.value.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
};

const handleMouseMove = () => {
  showControls.value = true;
  clearTimeout(controlTimer);
  controlTimer = setTimeout(() => {
    if (isPlaying.value) showControls.value = false;
  }, 3000);
};

const handleKeydown = (e) => {
  if (e.code === 'Space') {
    e.preventDefault(); 
    togglePlay();
  }
};

const setCurrentTime = (time) => {
  const video = videoRef.value;
  if (!video) return;
  const doSeek = () => {
    if (typeof time === 'number' && time > 0) video.currentTime = time;
  };
  if (video.readyState >= 1) {
    doSeek();
  } else {
    const handler = () => { doSeek(); video.removeEventListener('loadedmetadata', handler); };
    video.addEventListener('loadedmetadata', handler);
  }
};

const playVideo = async () => {
  if (!videoRef.value) return;
  try {
    await videoRef.value.play();
    isPlaying.value = true;
  } catch (err) {
    console.warn("Autoplay blocked", err);
    videoRef.value.muted = true;
    isMuted.value = true;
    await videoRef.value.play();
    isPlaying.value = true;
  }
};

defineExpose({ setCurrentTime, playVideo });
onMounted(() => { document.addEventListener('keydown', handleKeydown); });
onBeforeUnmount(() => { document.removeEventListener('keydown', handleKeydown); });

watch(() => props.src, () => { isPlaying.value = false; currentPercentage.value = 0; });
</script>

<style scoped>
/* ... existing styles ... */
.custom-player {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000;
  overflow: hidden;
  user-select: none;
  font-family: Roboto, Arial, sans-serif;
}
.custom-player.hide-cursor { cursor: none; }

.video-element { width: 100%; height: 100%; display: block; }

.center-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.3);
  cursor: pointer;
  z-index: 10;
}
.play-icon-bg {
  width: 60px; height: 60px; border-radius: 50%;
  background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px);
}

.controls-bar {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  padding: 0 12px 12px;
  opacity: 0; transition: opacity 0.3s;
  display: flex; flex-direction: column; gap: 8px;
  z-index: 20;
}
.controls-bar.visible { opacity: 1; }

.progress-container {
  height: 5px; width: 100%; background: rgba(255,255,255,0.2);
  cursor: pointer; position: relative; border-radius: 2px;
  transition: height 0.1s;
  height: 6px; 
  transition: height 0.1s;
}
.progress-container:hover { height: 10px; }
.progress-buffered {
  position: absolute; height: 100%; background: rgba(255,255,255,0.4); left: 0; top: 0;
}
.progress-current {
  position: absolute; height: 100%; background: #FF0000; left: 0; top: 0;
  display: flex; align-items: center;
}
.progress-handle {
  width: 12px; height: 12px; border-radius: 50%; background: #FF0000;
  margin-left: auto; transform: scale(0); transition: transform 0.1s;
  margin-right: -6px; 
}
.progress-container:hover .progress-handle { transform: scale(1); }

.controls-row { display: flex; justify-content: space-between; align-items: center; color: white; }
.left-controls, .right-controls { display: flex; align-items: center; gap: 16px; }
.ctrl-btn { cursor: pointer; transition: transform 0.1s; }
.ctrl-btn:hover { transform: scale(1.1); }
.time-display { font-size: 13px; margin-left: 5px; }

.volume-box { display: flex; align-items: center; gap: 8px; }
.volume-slider { width: 0; overflow: hidden; transition: width 0.2s; height: 4px; accent-color: white; }
.volume-box:hover .volume-slider { width: 60px; }

/* End Screen Styles */
.end-screen-overlay {
    position: absolute; top: 10%; bottom: 15%; left: 5%; right: 5%;
    pointer-events: none; /* Let clicks pass through if empty areas? No, cards need clicks */
    display: flex; align-items: center; justify-content: center;
    z-index: 5;
}
.end-screen-content {
    width: 100%; height: 100%;
    pointer-events: auto; 
    display: flex;
    justify-content: flex-end; /* Align right like youtube */
    align-items: center;
    gap: 20px;
}
.end-grid { display: flex; gap: 20px; }
.end-card {
    width: 200px;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.2s, background 0.2s;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    display: flex; flex-direction: column;
}
.end-card:hover { transform: scale(1.05); background: rgba(255,255,255,0.2); }
.end-card-img { width: 100%; aspect-ratio: 16/9; position: relative; }
.end-card-img img { width: 100%; height: 100%; object-fit: cover; }
.end-duration { position: absolute; bottom: 4px; right: 4px; background: rgba(0,0,0,0.8); color: white; font-size: 10px; padding: 1px 4px; border-radius: 2px; }
.end-card-info { padding: 8px; }
.end-title { font-size: 12px; font-weight: bold; color: white; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.end-author { font-size: 10px; color: #ccc; }

/* Post Roll Styles */
.post-roll-overlay {
    position: absolute; top: 0; left: 0; right: 0; bottom: 40px; /* Above controls */
    background: rgba(0,0,0,0.85);
    z-index: 15;
    display: flex; flex-direction: column; padding: 20px;
}
.post-roll-header { color: #fff; font-size: 16px; margin-bottom: 15px; font-weight: bold; }
.post-roll-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 15px;
    overflow-y: auto; flex: 1;
}
.post-card {
    cursor: pointer; display: flex; flex-direction: column; gap: 5px;
}
.post-card:hover .post-thumb img { opacity: 0.8; }
.post-thumb { width: 100%; aspect-ratio: 16/9; position: relative; border-radius: 4px; overflow: hidden; }
.post-thumb img { width: 100%; height: 100%; object-fit: cover; }
.post-duration { position: absolute; bottom: 4px; right: 4px; background: rgba(0,0,0,0.8); color: white; font-size: 10px; padding: 1px 4px; border-radius: 2px; }
.post-info { color: #fff; }
.post-title { font-size: 13px; font-weight: 500; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 2px; }
.post-author { font-size: 11px; color: #aaa; }

.post-replay-btn {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    color: white; font-size: 14px; cursor: pointer;
    background: rgba(0,0,0,0.6); padding: 20px; border-radius: 50%; width: 80px; height: 80px;
    border: 2px solid rgba(255,255,255,0.3);
    backdrop-filter: blur(5px);
    transition: transform 0.2s, background 0.2s;
}
.post-replay-btn:hover { transform: translate(-50%, -50%) scale(1.1); background: rgba(0,0,0,0.8); }
.post-replay-btn .el-icon { font-size: 32px; margin-bottom: 5px; }
</style>