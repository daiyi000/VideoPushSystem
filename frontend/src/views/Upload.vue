<template>
  <div class="upload-container">
    <div class="upload-card">
      <h2 class="page-title">上传视频</h2>
      
      <el-form :model="form" label-position="top">
        <el-form-item label="视频文件">
          <div class="file-drop-zone" @click="triggerFile">
            <el-icon size="40" color="#ccc"><UploadFilled /></el-icon>
            <p v-if="!selectedFile">点击选择视频文件</p>
            <p v-else class="file-name">{{ selectedFile.name }}</p>
          </div>
          <input type="file" ref="fileInput" accept="video/*" style="display: none" @change="handleFileChange" />
        </el-form-item>

        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="添加引人注目的标题" />
        </el-form-item>
        
        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="告诉观众视频的内容" />
        </el-form-item>
        
        <el-form-item label="分类">
          <el-radio-group v-model="form.category">
            <el-radio-button label="科技" />
            <el-radio-button label="生活" />
            <el-radio-button label="娱乐" />
            <el-radio-button label="教育" />
            <el-radio-button label="电影" />
          </el-radio-group>
        </el-form-item>
        
        <div class="actions">
          <el-button type="primary" size="large" @click="submitUpload" :loading="loading" style="width: 100%; border-radius: 8px;">
            发布视频
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '../store/user';
import { uploadVideo } from '../api/video';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { UploadFilled } from '@element-plus/icons-vue';

const userStore = useUserStore();
const router = useRouter();
const loading = ref(false);
const selectedFile = ref(null);
const fileInput = ref(null);

const form = ref({ title: '', category: '生活', description: '' });

const triggerFile = () => fileInput.value.click();
const handleFileChange = (e) => { selectedFile.value = e.target.files[0]; };

const submitUpload = async () => {
  if (!userStore.token) return ElMessage.warning('请先登录');
  if (!selectedFile.value) return ElMessage.warning('请选择视频');
  if (!form.value.title) return ElMessage.warning('请输入标题');
  
  loading.value = true;
  const formData = new FormData();
  formData.append('file', selectedFile.value);
  formData.append('title', form.value.title);
  formData.append('category', form.value.category);
  formData.append('description', form.value.description);
  formData.append('uploader_id', userStore.userInfo.id);

  try {
    const res = await uploadVideo(formData);
    if (res.data.code === 200) {
      ElMessage.success('发布成功，正在转码中...');
      router.push('/profile');
    } else {
      ElMessage.error(res.data.msg);
    }
  } catch (error) {
    ElMessage.error('上传失败');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.upload-container { display: flex; justify-content: center; padding-top: 40px; }
.upload-card { width: 800px; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
.page-title { margin-top: 0; margin-bottom: 30px; text-align: center; color: #0f0f0f; }

.file-drop-zone { border: 2px dashed #d9d9d9; border-radius: 12px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; transition: border-color 0.2s; background: #fafafa; }
.file-drop-zone:hover { border-color: #409EFF; background: #f0f9ff; }
.file-name { color: #409EFF; font-weight: bold; margin-top: 10px; }
</style>