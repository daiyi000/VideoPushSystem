<template>
  <div class="upload-container">
    <el-card>
      <h2>发布视频</h2>
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="给视频起个标题"></el-input>
        </el-form-item>
        
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="选择分类">
            <el-option label="科技" value="科技"></el-option>
            <el-option label="生活" value="生活"></el-option>
            <el-option label="娱乐" value="娱乐"></el-option>
            <el-option label="教育" value="教育"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="简介">
          <el-input type="textarea" v-model="form.description" :rows="3"></el-input>
        </el-form-item>
        
        <el-form-item label="视频文件">
          <input type="file" @change="handleFileChange" accept="video/*" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitUpload" :loading="loading">立即发布</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '../store/user';
import { uploadVideo } from '../api/video';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const userStore = useUserStore();
const router = useRouter();
const loading = ref(false);
const selectedFile = ref(null);

const form = ref({
  title: '',
  category: '',
  description: ''
});

const handleFileChange = (e) => {
  selectedFile.value = e.target.files[0];
};

const submitUpload = async () => {
  if (!userStore.token) return ElMessage.warning('请先登录');
  if (!selectedFile.value) return ElMessage.warning('请选择视频文件');
  
  loading.value = true;
  const formData = new FormData();
  formData.append('file', selectedFile.value);
  formData.append('title', form.value.title);
  formData.append('category', form.value.category);
  formData.append('description', form.value.description);
  formData.append('uploader_id', userStore.userInfo.id); // 绑定当前用户

  try {
    const res = await uploadVideo(formData);
    if (res.data.code === 200) {
      ElMessage.success('发布成功！');
      router.push('/');
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
.upload-container { max-width: 600px; margin: 20px auto; }
</style>