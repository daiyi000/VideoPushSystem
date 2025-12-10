<template>
  <div class="home-container">
    
    <!-- 1. 吸顶分类栏 (使用组件) -->
    <FilterBar 
      v-if="!isSearch" 
      :categories="categories" 
      v-model="currentCategory" 
      @change="changeCategory" 
    />

    <!-- 内部内容容器 (增加 padding 以补偿 MainLayout 移除的 padding) -->
    <div class="home-content-inner">
      
      <!-- 2. 搜索结果 -->
      <div v-if="isSearch">
        <div class="search-filter-bar">
           <el-icon><Filter /></el-icon> 搜索结果：{{ videoList.length }} 条相关视频
        </div>
        <div class="video-list-wrapper search-mode">
          <div v-for="video in videoList" :key="video.id" class="video-card list-card" @click="goToDetail(video.id)">
            <div class="thumbnail-wrapper">
              <img :src="video.cover_url" class="thumbnail" />
              <span class="duration">{{ formatTime(video.duration) }}</span>
            </div>
            <div class="video-info">
              <img :src="video.uploader_avatar" class="uploader-avatar" />
              <div class="text-info">
                <h3 class="video-title" :title="video.title">{{ video.title }}</h3>
                <div class="video-meta">
                  {{ formatCount(video.views) }}次观看 • {{ formatDate(video.upload_time) }}
                </div>
                <div class="search-channel-row">
                  <img :src="video.uploader_avatar" class="search-avatar" />
                  <span class="search-author">{{ video.uploader_name }}</span>
                </div>
                <div class="search-desc">{{ video.description || '暂无简介' }}</div>
              </div>
            </div>
          </div>
        </div>
        <el-empty v-if="videoList.length === 0" description="没有找到相关视频" />
      </div>

      <!-- 3. 首页多版块布局 -->
      <div v-else class="home-sections">
        
        <!-- 版块 A: 推荐视频 -->
        <div class="section-container" v-if="discoverList && discoverList.length > 0">
          <div class="video-grid grid-3-cols">
            <div v-for="video in discoverList" :key="video.id" class="video-card horizontal-card" @click="goToDetail(video.id)">
               <div class="thumbnail-wrapper">
                  <img :src="video.cover_url" class="thumbnail" />
                  <span class="duration">{{ formatTime(video.duration) }}</span>
                </div>
                <div class="video-info">
                  <img :src="video.uploader_avatar" class="uploader-avatar" />
                  <div class="text-info">
                    <h3 class="video-title" :title="video.title">{{ video.title }}</h3>
                    <div class="channel-name">{{ video.uploader_name }}</div>
                    <div class="video-meta">{{ formatCount(video.views) }}次观看 • {{ formatDate(video.upload_time) }}</div>
                  </div>
                </div>
            </div>
          </div>
        </div>

        <!-- 版块 B: Shorts -->
        <div class="section-container" v-if="shortsList && shortsList.length > 0">
          <div class="section-header shorts-header">
             <el-icon color="#FF0000" size="24" style="margin-right:5px"><VideoPlay /></el-icon>
             <h3>Shorts</h3>
          </div>
          <div class="video-grid grid-5-cols">
             <div v-for="video in shortsList" :key="'shorts-'+video.id" class="video-card vertical-card" @click="goToShorts(video.id)">
                  <div class="thumbnail-wrapper vertical">
                    <img :src="video.cover_url" class="thumbnail" />
                    <div class="shorts-overlay">
                      <span class="shorts-views">{{ formatCount(video.views) }} 观看</span>
                    </div>
                  </div>
                  <div class="video-info">
                    <div class="text-info">
                      <h3 class="video-title">{{ video.title }}</h3>
                    </div>
                  </div>
             </div>
          </div>
        </div>

        <!-- 版块 C: 继续观看 -->
        <div class="section-container" v-if="historyList && historyList.length > 0">
          <div class="section-header"><h3>继续观看</h3></div>
          <div class="video-grid grid-3-cols">
             <div v-for="video in historyList" :key="'hist-'+video.id" class="video-card horizontal-card" @click="goToDetail(video.id)">
                  <div class="thumbnail-wrapper">
                    <img :src="video.cover_url" class="thumbnail" />
                    <div class="progress-bar-bg">
                      <div class="progress-bar-fill" :style="{ width: (video.progress_percent || 0) + '%' }"></div>
                    </div>
                    <span class="duration">{{ formatTime(video.duration) }}</span>
                  </div>
                  <div class="video-info">
                    <div class="text-info" style="margin-left:0">
                      <h3 class="video-title">{{ video.title }}</h3>
                      <div class="channel-name">{{ video.uploader_name }}</div>
                      <div class="video-meta">上次观看于刚刚</div>
                    </div>
                  </div>
             </div>
          </div>
        </div>

      </div>

      <el-empty v-if="!loading && (!discoverList || discoverList.length === 0) && (!shortsList || shortsList.length === 0) && !isSearch" description="这里空空如也" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '../store/user';
import { getVideoList } from '../api/video';
import { getRecommendVideos } from '../api/recommend';
import { Filter, VideoPlay } from '@element-plus/icons-vue';
// 引入新组件
import FilterBar from '../components/FilterBar.vue';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const videoList = ref([]); 
const currentCategory = ref('全部');
const categories = ref(['全部', '科技', '生活', '娱乐', '教育', '电影', '音乐', '游戏']);
const loading = ref(false);

const isSearch = computed(() => !!route.query.q);
const discoverList = ref([]);
const shortsList = ref([]);
const recentList = ref([]);
const historyList = ref([]);

const formatTime = (seconds) => {
  if (!seconds) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
};

const formatDate = (timeStr) => timeStr ? timeStr.split(' ')[0] : '';
const formatCount = (num) => num >= 10000 ? (num/10000).toFixed(1) + '万' : num;

const fetchData = async () => {
  loading.value = true;
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
        categories.value = d.categories || categories.value;
        discoverList.value = d.discover || [];
        shortsList.value = d.shorts || [];
        recentList.value = d.recent || [];
        historyList.value = d.history || [];
      }
    }
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

const changeCategory = (cat) => {
  currentCategory.value = cat;
  if(route.query.q) { router.push('/'); } else if (cat === '全部') { fetchData(); } else {
      getVideoList({ category: cat }).then(res => {
          discoverList.value = res.data.data;
          shortsList.value = [];
          historyList.value = [];
          recentList.value = [];
      });
  }
};

const goToDetail = (id) => { router.push(`/video/${id}`); };
const goToShorts = (id) => { router.push(`/shorts/${id}`); }

watch(() => route.query, fetchData);
onMounted(fetchData);
</script>

<style scoped>
/* 整个 Home 容器最大宽度 */
.home-container { width: 100%; }

/* 内容区域 padding，因为 MainLayout 移除了 padding */
.home-content-inner { padding: 0 24px 40px 24px; max-width: 2200px; margin: 0 auto; }

.search-filter-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; font-size: 16px; font-weight: 500; color: #0f0f0f; border-bottom: 1px solid #e5e5e5; padding-bottom: 10px; }

/* Grid 系统 */
.video-grid { display: grid; gap: 20px; row-gap: 40px; }
.grid-3-cols { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
.grid-5-cols { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }

/* 卡片样式 */
.video-card { cursor: pointer; transition: transform 0.2s; display: flex; flex-direction: column; }

.horizontal-card .thumbnail-wrapper { position: relative; width: 100%; aspect-ratio: 16 / 9; border-radius: 12px; overflow: hidden; background: #e5e5e5; margin-bottom: 12px; }
.horizontal-card:hover .thumbnail-wrapper { border-radius: 0; transition: border-radius 0.3s; }

.vertical-card .thumbnail-wrapper { position: relative; width: 100%; aspect-ratio: 9 / 16; border-radius: 12px; overflow: hidden; background: #e5e5e5; margin-bottom: 8px; }

.thumbnail { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.video-card:hover .thumbnail { transform: scale(1.05); }
.duration { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: white; padding: 3px 4px; border-radius: 4px; font-size: 12px; font-weight: 500; }

.shorts-overlay { position: absolute; bottom: 0; left: 0; right: 0; top: 0; background: linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 30%); display: flex; flex-direction: column; justify-content: flex-end; padding: 10px; }
.shorts-views { color: white; font-size: 12px; font-weight: bold; }

.progress-bar-bg { position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background: rgba(255,255,255,0.3); }
.progress-bar-fill { height: 100%; background: red; }

.video-info { display: flex; gap: 12px; align-items: flex-start; }
.uploader-avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; background: #ddd; }
.text-info { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.video-title { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #0f0f0f; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.channel-name, .video-meta { font-size: 14px; color: #606060; }
.channel-name:hover { color: #0f0f0f; }

.search-mode { display: flex; flex-direction: column; max-width: 1000px; margin: 0 auto; gap: 16px; }
.search-mode .video-card { flex-direction: row; gap: 16px; align-items: flex-start; }
.search-mode .thumbnail-wrapper { width: 360px; max-width: 40%; height: auto; aspect-ratio: 16 / 9; margin-bottom: 0; }
.search-mode .video-info { flex: 1; gap: 0; }
.search-mode .video-title { font-size: 18px; margin-bottom: 6px; }
.search-channel-row { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; color: #606060; font-size: 12px; }
.search-avatar { width: 24px; height: 24px; border-radius: 50%; object-fit: cover; }
.search-author:hover { color: #0f0f0f; }
.search-desc { font-size: 12px; color: #606060; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

@media screen and (max-width: 768px) { 
  .search-mode .thumbnail-wrapper { width: 160px; max-width: none; } 
  .search-mode .video-title { font-size: 14px; } 
  .search-desc { display: none; } 
}

.home-sections { display: flex; flex-direction: column; gap: 40px; margin-top: 20px; }
.section-header { display: flex; align-items: center; margin-bottom: 16px; }
.section-header h3 { margin: 0; font-size: 20px; font-weight: 700; color: #0f0f0f; }
.shorts-header { gap: 8px; color: #0f0f0f; }
</style>