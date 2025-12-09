<template>
  <div>
    <el-dialog 
      v-model="visible" 
      width="960px" 
      :show-close="false" 
      class="yt-edit-modal" 
      align-center 
      destroy-on-close
      :close-on-click-modal="false"
    >
      <template #header>
        <div class="edit-header">
           <span class="header-title">{{ form.title || '视频详情' }}</span>
           <div class="header-btns">
              <el-button round @click="handleClose">取消更改</el-button>
              <el-button type="primary" round @click="save" :loading="loading">保存</el-button>
              <el-dropdown trigger="click" @command="handleMenuCommand">
                 <el-icon class="more-btn"><MoreFilled /></el-icon>
                 <template #dropdown>
                   <el-dropdown-menu>
                     <el-dropdown-item command="delete" style="color:red">永久删除</el-dropdown-item>
                   </el-dropdown-menu>
                 </template>
              </el-dropdown>
           </div>
        </div>
      </template>
      
      <div class="edit-body" v-loading="loadingData">
         <!-- 左侧：表单 -->
         <div class="edit-left">
            <div class="yt-input-box">
              <label>标题 (必填)</label>
              <el-input v-model="form.title" type="textarea" autosize maxlength="100" show-word-limit />
            </div>
            <div class="yt-input-box mt-4">
              <label>说明</label>
              <el-input v-model="form.description" type="textarea" :rows="8" maxlength="5000" show-word-limit />
            </div>
            
            <div class="form-section-title mt-4">缩略图</div>
            <div class="thumb-selector">
               <div class="thumb-preview-box" @click="triggerCoverChange">
                  <img v-if="form.cover_url" :src="form.cover_url" class="thumb-img">
                  <div class="thumb-overlay"><el-icon><Picture /></el-icon> 更改</div>
               </div>
               <div class="helper-text">点击图片以上传新封面</div>
            </div>

            <div class="form-section-title mt-4">分类</div>
            <el-select v-model="form.category" placeholder="选择分类" style="width:100%">
               <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
            </el-select>
            
            <div class="form-section-title mt-4">标签</div>
            <el-input v-model="form.tags" placeholder="输入标签，用逗号分隔" />
         </div>
         
         <!-- 右侧：预览与设置 -->
         <div class="edit-right">
            <div class="preview-player-card">
               <video v-if="videoUrl" :src="videoUrl" controls class="preview-video"></video>
               <div class="preview-meta">
                  <div class="meta-row"><span class="label">视频链接</span> <span class="val link">/video/{{ videoId }}</span></div>
                  <div class="meta-row"><span class="label">文件名</span> <span class="val">{{ form.title }}.mp4</span></div>
               </div>
            </div>
            
            <div class="setting-box">
               <div class="setting-label">公开范围</div>
               <el-select v-model="form.visibility" style="width:100%">
                  <el-option label="公开" value="public"><div class="vis-opt"><el-icon><View /></el-icon> 公开</div></el-option>
                  <el-option label="私享" value="private"><div class="vis-opt"><el-icon><Lock /></el-icon> 私享</div></el-option>
               </el-select>
               <div class="audit-warning">
                  <el-icon><Warning /></el-icon> 修改标题、简介或可见性后，视频需<b>重新审核</b>。
               </div>
            </div>
         </div>
      </div>
    </el-dialog>

    <!-- 图片裁剪组件 -->
    <ImageCropper ref="cropperRef" title="更换封面" :aspect-ratio="16/9" @upload="doUploadCover" />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { getVideoDetail, updateVideo, deleteVideo } from '../api/video';
import { uploadBanner } from '../api/user'; // 复用上传图片
import { ElMessage, ElMessageBox } from 'element-plus';
import { MoreFilled, Picture, View, Lock, Warning, Camera } from '@element-plus/icons-vue';
import ImageCropper from './ImageCropper.vue';
import { useUserStore } from '../store/user';
import { useRouter } from 'vue-router';

const emit = defineEmits(['saved', 'deleted']);
const userStore = useUserStore();
const router = useRouter();

const visible = ref(false);
const loading = ref(false);
const loadingData = ref(false);
const videoId = ref(null);
const videoUrl = ref('');
const cropperRef = ref(null);

const form = reactive({
  title: '',
  description: '',
  visibility: 'public',
  category: '',
  tags: '',
  cover_url: ''
});

const categories = ["宠物和动物", "电影和动画", "公益和社会活动", "教育", "科学和技术", "旅游和活动", "汽车和其他交通工具", "人物和博客", "体育", "喜剧", "新闻和政治", "音乐", "游戏", "娱乐", "DIY和生活百科"];

// 对外暴露的打开方法
const open = async (id) => {
  videoId.value = id;
  visible.value = true;
  loadingData.value = true;
  
  try {
    const res = await getVideoDetail(id);
    if (res.data.code === 200) {
      const v = res.data.data;
      form.title = v.title;
      form.description = v.description;
      form.visibility = v.visibility;
      form.category = v.category;
      form.tags = v.tags;
      form.cover_url = v.cover_url;
      videoUrl.value = v.url;
    }
  } catch (e) {
    ElMessage.error('获取视频信息失败');
    visible.value = false;
  } finally {
    loadingData.value = false;
  }
};

// 保存更改
const save = async () => {
  if (!form.title) return ElMessage.warning('标题不能为空');
  
  loading.value = true;
  try {
    const res = await updateVideo({
      id: videoId.value,
      user_id: userStore.userInfo.id,
      ...form
    });
    
    if (res.data.code === 200) {
      ElMessage.success('保存成功，已提交审核');
      visible.value = false;
      emit('saved'); // 通知父组件刷新数据
    } else {
      ElMessage.error(res.data.msg);
    }
  } catch (e) {
    ElMessage.error('保存失败');
  } finally {
    loading.value = false;
  }
};

// 删除视频
const handleMenuCommand = (cmd) => {
  if (cmd === 'delete') {
    ElMessageBox.confirm('确定永久删除此视频？', '警告', { type: 'warning' }).then(async () => {
      await deleteVideo(videoId.value);
      ElMessage.success('已删除');
      visible.value = false;
      emit('deleted'); // 通知父组件
    });
  }
};

// 封面上传逻辑
const triggerCoverChange = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.onchange = (e) => {
    if (e.target.files[0]) cropperRef.value.open(e.target.files[0]);
  };
  input.click();
};

const doUploadCover = async (blob, done) => {
  const formData = new FormData();
  formData.append('file', blob, 'cover.jpg');
  try {
    const res = await uploadBanner(formData);
    if (res.data.code === 200) {
      form.cover_url = res.data.url;
      done();
    }
  } catch (e) { ElMessage.error('上传失败'); }
};

const handleClose = () => {
    visible.value = false;
};

defineExpose({ open });
</script>

<style scoped>
:deep(.yt-edit-modal) { border-radius: 12px; overflow: hidden; margin-top: 5vh !important; }
:deep(.el-dialog__header) { padding: 0; margin: 0; }
:deep(.el-dialog__body) { padding: 0; }

.edit-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 24px; border-bottom: 1px solid #eee; }
.header-title { font-size: 20px; font-weight: 600; }
.header-btns { display: flex; align-items: center; gap: 10px; }
.more-btn { cursor: pointer; font-size: 20px; color: #606060; margin-left: 10px; }

.edit-body { display: flex; height: 70vh; } /* 固定高度 */
.edit-left { flex: 1; padding: 24px; overflow-y: auto; border-right: 1px solid #eee; }
.edit-right { width: 320px; padding: 24px; background: #f9f9f9; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }

.yt-input-box { border: 1px solid #ccc; border-radius: 4px; padding: 10px; transition: border-color 0.2s; }
.yt-input-box:focus-within { border-color: #065fd4; }
.yt-input-box label { font-size: 12px; color: #606060; display: block; margin-bottom: 4px; }
:deep(.el-input__wrapper), :deep(.el-textarea__inner) { box-shadow: none !important; padding: 0; font-size: 15px; color: #0f0f0f; }

.mt-4 { margin-top: 20px; }
.form-section-title { font-weight: 500; margin-bottom: 8px; color: #0f0f0f; font-size: 14px; }

.thumb-selector { margin-bottom: 20px; }
.thumb-preview-box { width: 192px; aspect-ratio: 16/9; background: #eee; border-radius: 4px; overflow: hidden; cursor: pointer; position: relative; border: 1px solid #ddd; }
.thumb-img { width: 100%; height: 100%; object-fit: cover; }
.thumb-overlay { position: absolute; top:0; left:0; right:0; bottom:0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; color: white; opacity: 0; transition: opacity 0.2s; gap: 5px; font-size: 13px; }
.thumb-preview-box:hover .thumb-overlay { opacity: 1; }
.helper-text { font-size: 12px; color: #606060; margin-top: 5px; }

.preview-player-card { background: #f0f0f0; border-radius: 4px; overflow: hidden; }
.preview-video { width: 100%; aspect-ratio: 16/9; background: #000; }
.preview-meta { padding: 12px; }
.meta-row { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px; }
.meta-row .label { color: #606060; }
.meta-row .val { font-weight: 500; color: #0f0f0f; text-align: right; word-break: break-all; }
.meta-row .val.link { color: #065fd4; }

.setting-box { background: white; padding: 15px; border-radius: 4px; border: 1px solid #e5e5e5; }
.setting-label { font-size: 14px; font-weight: 500; margin-bottom: 10px; color: #0f0f0f; }
.vis-opt { display: flex; align-items: center; gap: 5px; }
.audit-warning { font-size: 12px; color: #E6A23C; margin-top: 10px; display: flex; align-items: flex-start; gap: 5px; background: #fdf6ec; padding: 8px; border-radius: 4px; line-height: 1.4; }
</style>