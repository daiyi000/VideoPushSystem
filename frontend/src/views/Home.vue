<template>
  <div class="home-container">
    <div class="tags-bar" v-if="!isSearch">
      <div v-for="cat in categories" :key="cat" :class="['tag-pill', { active: currentCategory === cat }]" @click="changeCategory(cat)">{{ cat }}</div>
    </div>
    <div v-if="isSearch" class="search-filter-bar"><el-icon><Filter /></el-icon> 搜索结果：{{ videoList.length }} 条相关视频</div>
    <div :class="['video-list-wrapper', { 'search-mode': isSearch }]">
      <div v-for="video in videoList" :key="video.id" class="video-card" @click="goToDetail(video.id)">
        <div class="thumbnail-wrapper">
          <img :src="video.cover_url" class="thumbnail" />
          <!-- 【修复】显示真实时长 -->
          <span class="duration">{{ formatTime(video.duration) }}</span>
        </div>
        <div class="video-info">
          <img v-if="!isSearch" :src="video.uploader_avatar" class="uploader-avatar" />
          <div class="text-info">
            <h3 class="video-title" :title="video.title">{{ video.title }}</h3>
            <div class="video-meta" v-if="isSearch">{{ video.views }}次观看 • {{ video.upload_time.split(' ')[0] }}</div>
            <div class="search-channel-row" v-if="isSearch"><img :src="video.uploader_avatar" class="search-avatar" /><span class="search-author">{{ video.uploader_name }}</span></div>
            <div class="search-desc" v-if="isSearch">{{ video.description || '暂无简介' }}</div>
            <div v-if="!isSearch"><div class="channel-name">{{ video.uploader_name }}</div><div class="video-meta">{{ video.views }}次观看 • {{ video.upload_time.split(' ')[0] }}</div></div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="!isSearch" class="home-sections">
      <div class="section-header" v-if="discoverList.length > 0"><h3>发现</h3></div>
      <div class="video-grid" v-if="discoverList.length > 0">
        <div v-for="video in discoverList" :key="video.id" class="video-card" @click="goToDetail(video.id)">
           <div class="thumbnail-wrapper"><img :src="video.cover_url" class="thumbnail" /><span class="duration">{{ formatTime(video.duration) }}</span></div>
            <div class="video-info"><img :src="video.uploader_avatar" class="uploader-avatar" /><div class="text-info"><h3 class="video-title" :title="video.title">{{ video.title }}</h3><div class="channel-name">{{ video.uploader_name }}</div><div class="video-meta">{{ video.views }}次观看 • {{ video.upload_time.split(' ')[0] }}</div></div></div>
        </div>
      </div>
      <div class="section-header" v-if="historyList.length > 0"><h3>继续观看</h3></div>
      <div class="video-grid" v-if="historyList.length > 0">
         <div v-for="video in historyList" :key="video.id" class="video-card" @click="goToDetail(video.id)">
              <div class="thumbnail-wrapper"><img :src="video.cover_url" class="thumbnail" /><div class="progress-bar-bottom"></div><span class="duration">{{ formatTime(video.duration) }}</span></div>
              <div class="video-info"><div class="text-info" style="margin-left:0"><h3 class="video-title">{{ video.title }}</h3><div class="channel-name">{{ video.uploader_name }}</div></div></div>
         </div>
      </div>
      <div class="section-header" v-if="recentList.length > 0"><h3>最新发布</h3></div>
      <div class="video-grid" v-if="recentList.length > 0">
          <div v-for="video in recentList" :key="video.id" class="video-card" @click="goToDetail(video.id)">
               <div class="thumbnail-wrapper"><img :src="video.cover_url" class="thumbnail" /><span class="duration">{{ formatTime(video.duration) }}</span></div>
              <div class="video-info"><img :src="video.uploader_avatar" class="uploader-avatar" /><div class="text-info"><h3 class="video-title">{{ video.title }}</h3><div class="channel-name">{{ video.uploader_name }}</div><div class="video-meta">{{ video.views }}次观看 • 刚刚</div></div></div>
          </div>
      </div>
    </div>
    <el-empty v-if="videoList.length === 0 && discoverList.length === 0 && !isSearch" description="这里空空如也" />
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

const isSearch = computed(() => !!route.query.q);
const discoverList = ref([]);
const recentList = ref([]);
const historyList = ref([]);

// 【新增】时长格式化
const formatTime = (seconds) => {
  if (!seconds) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
};

const fetchData = async () => {
  const queryQ = route.query.q || '';
  try {
    if (queryQ) {
      const res = await getVideoList({ q: queryQ });
      videoList.value = res.data.data;
    } else {
      const uid = userStore.token ? userStore.userInfo.id : null;
      const res = await getRecommendVideos(uid); 
      if (res.data.code === 200) {
        const d = res.data.data;
        categories.value = d.categories;
        discoverList.value = d.discover;
        recentList.value = d.recent;
        historyList.value = d.history;
      }
    }
  } catch (e) { console.error(e); }
};

const changeCategory = (cat) => {
  currentCategory.value = cat;
  if(route.query.q) router.push('/');
  else {
      getVideoList({ category: cat }).then(res => {
          discoverList.value = res.data.data;
          recentList.value = [];
          historyList.value = [];
      });
  }
};
const goToDetail = (id) => { router.push(`/video/${id}`); };

watch(() => route.query, fetchData);
onMounted(fetchData);
</script>

<style scoped>
.home-container { max-width: 2000px; margin: 0 auto; }
.tags-bar { display: flex; gap: 12px; margin-bottom: 24px; overflow-x: auto; padding-bottom: 5px; }
.tag-pill { padding: 6px 12px; background: rgba(0,0,0,0.05); border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; white-space: nowrap; transition: all 0.2s; color: #0f0f0f; }
.tag-pill:hover { background: #e5e5e5; }
.tag-pill.active { background: #0f0f0f; color: white; }
.search-filter-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; font-size: 16px; font-weight: 500; color: #0f0f0f; border-bottom: 1px solid #e5e5e5; padding-bottom: 10px; }

.video-list-wrapper { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; row-gap: 40px; }
.video-card { cursor: pointer; transition: transform 0.2s; display: flex; flex-direction: column; }
.thumbnail-wrapper { position: relative; width: 100%; aspect-ratio: 16 / 9; border-radius: 12px; overflow: hidden; background: #e5e5e5; margin-bottom: 12px; flex-shrink: 0; }
.thumbnail { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.video-card:hover .thumbnail { transform: scale(1.05); }
.duration { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: white; padding: 3px 4px; border-radius: 4px; font-size: 12px; font-weight: 500; }
.video-info { display: flex; gap: 12px; align-items: flex-start; }
.uploader-avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; background: #ddd; }
.text-info { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.video-title { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #0f0f0f; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.channel-name, .video-meta { font-size: 14px; color: #606060; }
.channel-name:hover { color: #0f0f0f; }

.video-list-wrapper.search-mode { display: flex; flex-direction: column; max-width: 1000px; margin: 0 auto; gap: 16px; }
.search-mode .video-card { flex-direction: row; gap: 16px; align-items: flex-start; }
.search-mode .thumbnail-wrapper { width: 360px; max-width: 40%; height: auto; aspect-ratio: 16 / 9; margin-bottom: 0; }
.search-mode .video-info { flex: 1; gap: 0; }
.search-mode .video-title { font-size: 18px; margin-bottom: 6px; }
.search-mode .video-meta { font-size: 12px; margin-bottom: 12px; }
.search-channel-row { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; color: #606060; font-size: 12px; }
.search-avatar { width: 24px; height: 24px; border-radius: 50%; object-fit: cover; }
.search-author:hover { color: #0f0f0f; }
.search-desc { font-size: 12px; color: #606060; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
@media screen and (max-width: 768px) { .search-mode .thumbnail-wrapper { width: 160px; max-width: none; } .search-mode .video-title { font-size: 14px; } .search-desc { display: none; } }

.home-sections { display: flex; flex-direction: column; gap: 40px; margin-top: 20px; }
.section-header h3 { margin: 0 0 16px 0; font-size: 20px; font-weight: 700; color: #0f0f0f; }
.progress-bar-bottom { position: absolute; bottom: 0; left: 0; width: 60%; height: 3px; background: red; z-index: 2; }
.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
</style>