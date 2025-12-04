<template>
  <div class="home-container">
    <!-- 分类标签 -->
    <div class="tags-bar">
      <div 
        v-for="cat in categories" 
        :key="cat"
        :class="['tag-pill', { active: currentCategory === cat }]"
        @click="changeCategory(cat)"
      >
        {{ cat }}
      </div>
    </div>

    <!-- 视频网格 -->
    <div class="video-grid">
      <div v-for="video in videoList" :key="video.id" class="video-card" @click="goToDetail(video.id)">
        <div class="thumbnail-wrapper">
          <img :src="video.cover_url" class="thumbnail" />
          <span class="duration">12:30</span>
        </div>
        
        <div class="video-info">
          <img :src="video.uploader_avatar" class="uploader-avatar" />
          <div class="text-info">
            <h3 class="video-title" :title="video.title">{{ video.title }}</h3>
            <div class="channel-name">{{ video.uploader_name }}</div>
            <div class="video-meta">
              {{ video.views }}次观看 • {{ video.upload_time.split(' ')[0] }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="videoList.length === 0" description="这里空空如也" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '../store/user';
import { getVideoList } from '../api/video';
import { getRecommendVideos } from '../api/recommend';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const videoList = ref([]);
const currentCategory = ref('全部');
const categories = ['全部', '科技', '生活', '娱乐', '教育', '电影', '音乐', '游戏'];

// 获取数据
const fetchVideos = async () => {
  // 从路由 Query 获取搜索关键词
  const queryQ = route.query.q || '';
  
  try {
    // 只有在 "全部" 且 "无搜索" 时，才走随机推荐
    if (currentCategory.value === '全部' && !queryQ) {
      const uid = userStore.token ? userStore.userInfo.id : null;
      // 每次刷新，后端算法都会随机 shuffle
      const res = await getRecommendVideos(uid); 
      videoList.value = res.data.data;
    } else {
      // 有分类或有搜索
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
  // 清除搜索参数
  if(route.query.q) router.push('/');
  else fetchVideos();
};

const goToDetail = (id) => {
  router.push(`/video/${id}`);
};

// 监听路由参数变化 (比如在 Layout 的搜索框输入后，URL变了，这里要重新加载)
watch(() => route.query, () => {
  fetchVideos();
});

onMounted(() => {
  fetchVideos();
});
</script>

<style scoped>
/* 样式只保留核心内容区，因为外框由 Layout 接管 */
.tags-bar { display: flex; gap: 12px; margin-bottom: 24px; overflow-x: auto; padding-bottom: 5px; }
.tag-pill { padding: 6px 12px; background: rgba(0,0,0,0.05); border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; white-space: nowrap; transition: all 0.2s; color: #0f0f0f; }
.tag-pill:hover { background: #e5e5e5; }
.tag-pill.active { background: #0f0f0f; color: white; }

.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; row-gap: 40px; }
.video-card { cursor: pointer; transition: transform 0.2s; }
.thumbnail-wrapper { position: relative; width: 100%; aspect-ratio: 16 / 9; border-radius: 12px; overflow: hidden; background: #ccc; margin-bottom: 12px; }
.thumbnail { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.video-card:hover .thumbnail { transform: scale(1.05); }
.duration { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: white; padding: 3px 4px; border-radius: 4px; font-size: 12px; font-weight: 500; }

.video-info { display: flex; gap: 12px; align-items: flex-start; }
.uploader-avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; background: #ddd; }
.text-info { flex: 1; display: flex; flex-direction: column; }
.video-title { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #0f0f0f; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.channel-name { font-size: 14px; color: #606060; }
.video-meta { font-size: 14px; color: #606060; }
</style>