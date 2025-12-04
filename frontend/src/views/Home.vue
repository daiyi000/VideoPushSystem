<template>
  <div class="home-container">
    <!-- 分类标签 (仅在非搜索模式下显示，或者你可以选择一直显示) -->
    <div class="tags-bar" v-if="!isSearch">
      <div 
        v-for="cat in categories" 
        :key="cat"
        :class="['tag-pill', { active: currentCategory === cat }]"
        @click="changeCategory(cat)"
      >
        {{ cat }}
      </div>
    </div>

    <!-- 搜索结果提示 -->
    <div v-if="isSearch" class="search-filter-bar">
      <el-icon><Filter /></el-icon> 搜索结果：{{ videoList.length }} 条相关视频
    </div>

    <!-- 视频列表容器：通过 search-mode 类切换布局 -->
    <div :class="['video-list-wrapper', { 'search-mode': isSearch }]">
      <div v-for="video in videoList" :key="video.id" class="video-card" @click="goToDetail(video.id)">
        
        <!-- 1. 封面区域 -->
        <div class="thumbnail-wrapper">
          <img :src="video.cover_url" class="thumbnail" />
          <span class="duration">12:30</span>
        </div>
        
        <!-- 2. 信息区域 -->
        <div class="video-info">
          <!-- A. 首页模式：大头像在左侧 -->
          <img v-if="!isSearch" :src="video.uploader_avatar" class="uploader-avatar" />
          
          <div class="text-info">
            <!-- 标题 -->
            <h3 class="video-title" :title="video.title">
              {{ video.title }}
            </h3>
            
            <!-- B. 搜索模式：元数据行 (观看次数 • 时间) -->
            <div class="video-meta" v-if="isSearch">
              {{ video.views }}次观看 • {{ video.upload_time.split(' ')[0] }}
            </div>

            <!-- C. 搜索模式：频道信息行 (小头像 + 名字) -->
            <div class="search-channel-row" v-if="isSearch">
              <img :src="video.uploader_avatar" class="search-avatar" />
              <span class="search-author">{{ video.uploader_name }}</span>
            </div>

            <!-- D. 搜索模式：简介 (显示两行) -->
            <div class="search-desc" v-if="isSearch">
              {{ video.description || '暂无简介' }}
            </div>

            <!-- E. 首页模式：作者名 + 元数据 -->
            <div v-if="!isSearch">
              <div class="channel-name">{{ video.uploader_name }}</div>
              <div class="video-meta">
                {{ video.views }}次观看 • {{ video.upload_time.split(' ')[0] }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="videoList.length === 0" description="这里空空如也" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '../store/user';
import { getVideoList } from '../api/video';
import { getRecommendVideos } from '../api/recommend';
import { Filter } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const videoList = ref([]);
const currentCategory = ref('全部');
const categories = ['全部', '科技', '生活', '娱乐', '教育', '电影', '音乐', '游戏'];

// 【核心】判断是否处于搜索模式
const isSearch = computed(() => {
  return !!route.query.q; // 如果 URL 里有 q 参数，就是搜索模式
});

// 获取数据
const fetchVideos = async () => {
  const queryQ = route.query.q || '';
  
  try {
    if (currentCategory.value === '全部' && !queryQ) {
      const uid = userStore.token ? userStore.userInfo.id : null;
      const res = await getRecommendVideos(uid); 
      videoList.value = res.data.data;
    } else {
      const res = await getVideoList({
        category: currentCategory.value,
        q: queryQ
      });
      videoList.value = res.data.data;
    }
  } catch (e) {
    console.error(e);
  }
};

const changeCategory = (cat) => {
  currentCategory.value = cat;
  if(route.query.q) router.push('/');
  else fetchVideos();
};

const goToDetail = (id) => {
  router.push(`/video/${id}`);
};

watch(() => route.query, () => {
  fetchVideos();
});

onMounted(() => {
  fetchVideos();
});
</script>

<style scoped>
.home-container {
  max-width: 2000px; /* 大屏适配 */
  margin: 0 auto;
}

/* 分类标签 */
.tags-bar { display: flex; gap: 12px; margin-bottom: 24px; overflow-x: auto; padding-bottom: 5px; }
.tag-pill { padding: 6px 12px; background: rgba(0,0,0,0.05); border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; white-space: nowrap; transition: all 0.2s; color: #0f0f0f; }
.tag-pill:hover { background: #e5e5e5; }
.tag-pill.active { background: #0f0f0f; color: white; }

/* 搜索结果提示条 */
.search-filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 500;
  color: #0f0f0f;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 10px;
}

/* =========================================
   默认模式 (Grid Layout)
   ========================================= */
.video-list-wrapper {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  row-gap: 40px;
}

.video-card {
  cursor: pointer;
  transition: transform 0.2s;
  display: flex;
  flex-direction: column; /* 默认垂直排列 */
}

.thumbnail-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  background: #e5e5e5;
  margin-bottom: 12px;
  flex-shrink: 0;
}

.thumbnail { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.video-card:hover .thumbnail { transform: scale(1.05); }
.duration { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: white; padding: 3px 4px; border-radius: 4px; font-size: 12px; font-weight: 500; }

.video-info { display: flex; gap: 12px; align-items: flex-start; }
.uploader-avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; background: #ddd; }
.text-info { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.video-title { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #0f0f0f; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.channel-name, .video-meta { font-size: 14px; color: #606060; }
.channel-name:hover { color: #0f0f0f; }

/* =========================================
   搜索模式 (List Layout) - 类似 YouTube 搜索结果
   ========================================= */
.video-list-wrapper.search-mode {
  display: flex;
  flex-direction: column;
  max-width: 1000px; /* 搜索列表不需要太宽 */
  margin: 0 auto;
  gap: 16px; /* 卡片间距 */
}

.search-mode .video-card {
  flex-direction: row; /* 改为水平排列 */
  gap: 16px;
  align-items: flex-start;
}

/* 搜索模式下的封面 */
.search-mode .thumbnail-wrapper {
  width: 360px; /* 固定宽度 (大屏) */
  max-width: 40%; /* 移动端适配 */
  height: auto;
  aspect-ratio: 16 / 9;
  margin-bottom: 0; /* 去掉底部间距 */
}

/* 搜索模式下的信息区 */
.search-mode .video-info {
  flex: 1;
  gap: 0; /* 移除默认间距 */
}

.search-mode .video-title {
  font-size: 18px; /* 标题更大 */
  margin-bottom: 6px;
}

.search-mode .video-meta {
  font-size: 12px;
  margin-bottom: 12px;
}

/* 搜索频道的行 */
.search-channel-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #606060;
  font-size: 12px;
}
.search-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}
.search-author:hover { color: #0f0f0f; }

/* 搜索简介 */
.search-desc {
  font-size: 12px;
  color: #606060;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 限制显示2行 */
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 移动端适配搜索模式 */
@media screen and (max-width: 768px) {
  .search-mode .thumbnail-wrapper {
    width: 160px; /* 手机上封面小一点 */
    max-width: none;
  }
  .search-mode .video-title { font-size: 14px; }
  .search-desc { display: none; /* 手机上隐藏简介 */ }
}
</style>