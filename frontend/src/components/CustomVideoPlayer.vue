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
    ></video>

    <!-- 遮罩层：暂停时显示大图标 -->
    <div class="center-overlay" v-if="!isPlaying" @click="togglePlay">
       <div class="play-icon-bg">
         <el-icon size="40" color="#fff"><VideoPlay /></el-icon>
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
               <!-- 注意：Element Plus 没有专门的 Volume 图标，暂用 Microphone 或自定义 SVG -->
             </el-icon>
             <input type="range" min="0" max="1" step="0.1" v-model="volume" class="volume-slider" @input="updateVolume">
          </div>

          <div class="time-display">
            {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
          </div>
        </div>

        <div class="right-controls">
          <el-icon class="ctrl-btn" @click="toggleFullscreen" size="24"><FullScreen /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { VideoPlay, VideoPause, FullScreen, Microphone, Mute } from '@element-plus/icons-vue';

const props = defineProps({
  src: String,
  autoplay: { type: Boolean, default: false }
});

const emit = defineEmits(['timeupdate', 'play', 'pause', 'ended']);

const videoRef = ref(null);
const playerContainer = ref(null);

const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const currentPercentage = ref(0);
const bufferedPercentage = ref(0);
const volume = ref(1);
const isMuted = ref(false);
const showControls = ref(true);
let controlTimer = null;
const isDragging = ref(false); // 新增：标记是否正在拖拽
const progressRef = ref(null); // 新增：进度条容器 ref

// 格式化时间
const formatTime = (time) => {
  if (!time || isNaN(time)) return '0:00';
  const m = Math.floor(time / 60);
  const s = Math.floor(time % 60);
  return `${m}:${s < 10 ? '0' + s : s}`;
};

// 播放控制
const togglePlay = () => {
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

// 【新增】拖拽逻辑
const startDrag = (e) => {
  isDragging.value = true;
  handleDrag(e); // 立即更新一次位置
  // 添加全局监听，防止鼠标移出进度条后拖拽失效
  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('mouseup', stopDrag);
};

const handleDrag = (e) => {
  if (!duration.value) return;
  const rect = progressRef.value.getBoundingClientRect();
  let pos = (e.clientX - rect.left) / rect.width;
  // 限制范围 0-1
  pos = Math.max(0, Math.min(1, pos));
  
  currentPercentage.value = pos * 100;
  // 拖拽过程中，我们可以选择是否实时更新视频画面（scrubbing），这里选择实时更新
  videoRef.value.currentTime = pos * duration.value;
};

const stopDrag = (e) => {
  if (isDragging.value) {
    handleDrag(e); // 最后确认一次位置
    isDragging.value = false;
    document.removeEventListener('mousemove', handleDrag);
    document.removeEventListener('mouseup', stopDrag);
  }
};

const onLoadedMetadata = () => {
  duration.value = videoRef.value.duration;
  if (props.autoplay) togglePlay();
};

const onProgress = () => {
  if (videoRef.value.buffered.length > 0) {
    const bufferedEnd = videoRef.value.buffered.end(videoRef.value.buffered.length - 1);
    bufferedPercentage.value = (bufferedEnd / duration.value) * 100;
  }
};

const onEnded = () => {
  isPlaying.value = false;
  emit('ended');
};

// 进度条拖拽
const seek = (e) => {
  if(!isDragging.value) {
     const rect = progressRef.value.getBoundingClientRect();
     const pos = (e.clientX - rect.left) / rect.width;
     videoRef.value.currentTime = pos * duration.value;
  }
};

// 音量
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

// 全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    playerContainer.value.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
};

// 鼠标交互
const handleMouseMove = () => {
  showControls.value = true;
  clearTimeout(controlTimer);
  controlTimer = setTimeout(() => {
    if (isPlaying.value) showControls.value = false;
  }, 3000);
};

// 快捷键
const handleKeydown = (e) => {
  if (e.code === 'Space') {
    e.preventDefault(); // 防止页面滚动
    togglePlay();
  }
};

// 设置当前播放时间的方法
const setCurrentTime = (time) => {
  const video = videoRef.value;
  if (!video) return;

  const doSeek = () => {
    // 只有当时间有效且大于0时才跳转
    if (typeof time === 'number' && time > 0) {
      video.currentTime = time;
    }
  };

  // 如果元数据已加载，直接跳转；否则等待 loadedmetadata 事件
  if (video.readyState >= 1) {
    doSeek();
  } else {
    const handler = () => {
      doSeek();
      video.removeEventListener('loadedmetadata', handler);
    };
    video.addEventListener('loadedmetadata', handler);
  }
};
// 【新增】暴露给父组件的播放方法
const playVideo = async () => {
  if (!videoRef.value) return;
  try {
    // 尝试播放
    await videoRef.value.play();
    isPlaying.value = true;
  } catch (err) {
    console.warn("自动播放被拦截，尝试静音播放:", err);
    // 如果播放失败（通常是因为没有用户交互），尝试静音播放
    videoRef.value.muted = true;
    isMuted.value = true;
    await videoRef.value.play();
    isPlaying.value = true;
    // 提示用户
    // ElMessage.info('已自动静音播放，请手动开启声音');
  }
};

// 将方法暴露给父组件
defineExpose({
  setCurrentTime,
  playVideo // <--- 新增
});
onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
});
onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown);
});

// 监听 src 变化重置
watch(() => props.src, () => {
  isPlaying.value = false;
  currentPercentage.value = 0;
});

</script>

<style scoped>
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

/* 居中播放按钮 */
.center-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.3);
  cursor: pointer;
}
.play-icon-bg {
  width: 60px; height: 60px; border-radius: 50%;
  background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px);
}

/* 底部控制栏 */
.controls-bar {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  padding: 0 12px 12px;
  opacity: 0; transition: opacity 0.3s;
  display: flex; flex-direction: column; gap: 8px;
}
.controls-bar.visible { opacity: 1; }

/* 进度条 */
.progress-container {
  height: 5px; width: 100%; background: rgba(255,255,255,0.2);
  cursor: pointer; position: relative; border-radius: 2px;
  transition: height 0.1s;
  height: 6px; /*稍微加粗*/
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
  margin-right: -6px; /* Center handle at the end */
}
.progress-container:hover .progress-handle { transform: scale(1); }

/* 按钮行 */
.controls-row { display: flex; justify-content: space-between; align-items: center; color: white; }
.left-controls, .right-controls { display: flex; align-items: center; gap: 16px; }
.ctrl-btn { cursor: pointer; transition: transform 0.1s; }
.ctrl-btn:hover { transform: scale(1.1); }
.time-display { font-size: 13px; margin-left: 5px; }

/* 音量条 */
.volume-box { display: flex; align-items: center; gap: 8px; }
.volume-slider { width: 0; overflow: hidden; transition: width 0.2s; height: 4px; accent-color: white; }
.volume-box:hover .volume-slider { width: 60px; }
</style>