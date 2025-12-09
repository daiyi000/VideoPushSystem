<template>
  <div class="custom-page">
    <h3>频道自定义</h3>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="品牌形象" name="branding">
        <div class="section">
          <div class="section-head">头像</div>
          <div class="section-desc">此图片将显示在您的频道首页、您观看的视频旁以及评论中。</div>
          <div class="img-row">
            <el-avatar :size="100" :src="form.avatar" class="preview-avatar" />
            <div class="actions">
              <div class="helper">建议使用至少 98x98 像素的图片</div>
              <el-button type="primary" plain @click="triggerAvatar">更改</el-button>
              <input type="file" ref="avatarInput" hidden @change="e => onFileSelect(e, 'avatar')" accept="image/*">
            </div>
          </div>
        </div>

        <el-divider />

        <div class="section">
          <div class="section-head">横幅图片</div>
          <div class="section-desc">此图片将显示在您频道的顶部。</div>
          <div class="img-row">
            <div class="banner-preview-box">
               <img v-if="form.banner" :src="form.banner" class="banner-img">
               <div v-else class="banner-placeholder">暂无横幅</div>
            </div>
            <div class="actions">
              <div class="helper">为获得最佳效果，请使用至少 2048x1152 像素的图片</div>
              <el-button type="primary" plain @click="triggerBanner">更改</el-button>
              <input type="file" ref="bannerInput" hidden @change="e => onFileSelect(e, 'banner')" accept="image/*">
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="基本信息" name="info">
         <div class="form-wrapper">
            <div class="input-group">
              <label>名称</label>
              <el-input v-model="form.username" placeholder="输入频道名称" />
            </div>
            <div class="input-group">
              <label>说明</label>
              <el-input v-model="form.description" type="textarea" :rows="5" placeholder="向观众介绍您的频道" />
            </div>
            <div style="text-align: right; margin-top: 20px;">
               <el-button type="primary" @click="saveInfo">发布</el-button>
            </div>
         </div>
      </el-tab-pane>
    </el-tabs>

    <ImageCropper ref="cropperRef" :title="cropperTitle" :aspect-ratio="cropperRatio" @upload="handleUploadConfirm" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../../store/user';
import { updateProfile, uploadAvatar, uploadBanner } from '../../api/user';
import { ElMessage } from 'element-plus';
import ImageCropper from '../../components/ImageCropper.vue';

const userStore = useUserStore();
const activeTab = ref('branding');
const form = ref({ username: '', description: '', avatar: '', banner: '' });

const avatarInput = ref(null);
const bannerInput = ref(null);
const cropperRef = ref(null);
const cropperTitle = ref('');
const cropperRatio = ref(1);
const currentUploadType = ref('');

onMounted(() => {
  // 初始化数据
  form.value = { ...userStore.userInfo };
});

const triggerAvatar = () => avatarInput.value.click();
const triggerBanner = () => bannerInput.value.click();

const onFileSelect = (e, type) => {
  const file = e.target.files[0];
  if (!file) return;
  
  currentUploadType.value = type;
  if (type === 'avatar') {
    cropperTitle.value = '自定义头像';
    cropperRatio.value = 1;
  } else {
    cropperTitle.value = '自定义横幅';
    cropperRatio.value = 16 / 4; // 横幅比例
  }
  cropperRef.value.open(file);
  e.target.value = '';
};

const handleUploadConfirm = async (blob, done) => {
  const formData = new FormData();
  formData.append('file', blob, 'image.jpg');
  
  try {
    let res;
    if (currentUploadType.value === 'avatar') {
      res = await uploadAvatar(formData);
    } else {
      res = await uploadBanner(formData);
    }
    
    if (res.data.code === 200) {
      if (currentUploadType.value === 'avatar') form.value.avatar = res.data.url;
      else form.value.banner = res.data.url;
      
      // 立即更新用户信息保存 URL
      await saveInfo(); 
      done();
    }
  } catch (e) { ElMessage.error('上传失败'); }
};

const saveInfo = async () => {
  const res = await updateProfile({ user_id: userStore.userInfo.id, ...form.value });
  if (res.data.code === 200) {
    ElMessage.success('已发布更改');
    userStore.setLoginState(userStore.token, res.data.data);
  } else {
    ElMessage.error(res.data.msg);
  }
};
</script>

<style scoped>
.custom-page { padding: 0 20px; background: #fff; min-height: 100%; }
.section { margin-bottom: 30px; }
.section-head { font-size: 15px; color: #606060; margin-bottom: 5px; }
.section-desc { font-size: 13px; color: #909090; margin-bottom: 15px; }
.img-row { display: flex; gap: 30px; align-items: flex-start; }
.preview-avatar { border: 1px solid #eee; }
.banner-preview-box { width: 300px; height: 75px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; overflow: hidden; border-radius: 4px; }
.banner-img { width: 100%; height: 100%; object-fit: cover; }
.actions { display: flex; flex-direction: column; align-items: flex-start; gap: 10px; }
.helper { font-size: 12px; color: #909090; }
.form-wrapper { max-width: 600px; margin-top: 20px; }
.input-group { margin-bottom: 20px; }
.input-group label { display: block; font-size: 14px; font-weight: 500; margin-bottom: 8px; color: #0f0f0f; }
</style>