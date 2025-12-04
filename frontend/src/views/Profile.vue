<template>
  <div class="profile-container">
    <el-card>
      <div class="user-header">
        <el-avatar :size="80" :src="userInfo.avatar"></el-avatar>
        <div class="info">
          <h2>{{ userInfo.username }}</h2>
          <p v-if="userInfo.email">{{ userInfo.email }}</p>
          <p v-else style="color: #999; font-size: 12px;">暂无邮箱信息</p>
        </div>
      </div>

      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        
        <el-tab-pane label="我的发布" name="videos">
          <el-table :data="myVideos" style="width: 100%" empty-text="您还没有发布过视频">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column prop="upload_time" label="发布时间" />
            <el-table-column prop="views" label="播放量" width="100" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="我的收藏" name="favs">
          <div v-if="myFavs.length > 0" class="video-grid">
            <el-card 
              v-for="v in myFavs" 
              :key="v.id" 
              :body-style="{ padding: '0px', cursor: 'pointer' }" 
              @click="$router.push(`/video/${v.id}`)"
            >
              <img :src="v.cover_url" class="cover" />
              <div style="padding: 10px">
                <div class="video-title">{{ v.title }}</div>
              </div>
            </el-card>
          </div>
          <el-empty v-else description="暂无收藏" />
        </el-tab-pane>

        <el-tab-pane label="观看历史" name="history">
          <div v-if="myHistory.length > 0" style="padding: 20px;">
            <el-timeline>
              <el-timeline-item v-for="v in myHistory" :key="v.id" :timestamp="v.upload_time" placement="top">
                <el-card shadow="hover" @click="$router.push(`/video/${v.id}`)" style="cursor: pointer">
                  <h4>{{ v.title }}</h4>
                  <p style="color: #666; font-size: 12px; margin-top: 5px;">{{ v.description || '暂无简介' }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
          <el-empty v-else description="暂无观看历史" />
        </el-tab-pane>

        <el-tab-pane label="修改资料" name="settings">
          <el-form :model="editForm" label-width="80px" style="max-width: 400px; margin-top: 20px;">
            
            <el-form-item label="当前头像">
              <div class="avatar-uploader" @click="triggerFileInput">
                <img v-if="editForm.avatar" :src="editForm.avatar" class="avatar-preview" />
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
                <div class="upload-mask">点击修改</div>
              </div>
              <input type="file" ref="fileInput" style="display: none" accept="image/*" @change="handleAvatarUpload" />
            </el-form-item>

            <el-form-item label="用户名">
              <el-input v-model="editForm.username" placeholder="请输入用户名"></el-input>
            </el-form-item>

            <el-form-item label="新密码">
              <el-input v-model="editForm.password" type="password" placeholder="不填则不修改" show-password></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile">保存所有修改</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../store/user';
// 引入所有需要的 API
import { getMyVideos, getMyFavs, getMyHistory, updateProfile, uploadAvatar } from '../api/user';
import { deleteVideo } from '../api/video';
// 引入组件库工具
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';

const userStore = useUserStore();
const activeTab = ref('videos');
const userInfo = ref({ ...userStore.userInfo }); 

// 编辑表单数据
const editForm = ref({ 
  avatar: userStore.userInfo.avatar, 
  username: userStore.userInfo.username,
  password: '' 
});

// 数据列表
const myVideos = ref([]);
const myFavs = ref([]);
const myHistory = ref([]);
const fileInput = ref(null); // 指向 input DOM

// 1. 修改 loadData，让它支持接收参数
// currentTabName 是可选参数，如果不传，就默认用 activeTab.value
const loadData = async (currentTabName = null) => {
  const uid = userStore.userInfo.id;
  if (!uid) return;

  // 关键修正：优先使用传入的参数，没有传参才用 activeTab.value
  const tab = currentTabName || activeTab.value;

  try {
    if (tab === 'videos') {
      const res = await getMyVideos(uid);
      myVideos.value = res.data.data;
    } else if (tab === 'favs') {
      const res = await getMyFavs(uid);
      myFavs.value = res.data.data;
    } else if (tab === 'history') {
      const res = await getMyHistory(uid);
      myHistory.value = res.data.data;
    }
  } catch (error) {
    console.error('加载数据失败', error);
  }
};

// 2. 修改点击事件
// Element Plus 的 tab-click 事件会把 tab 实例传进来
const handleTabClick = (tabContext) => {
  // tabContext.props.name 就是你点的那个 Tab 的名字（videos/favs/history）
  // 我们直接把它传给 loadData
  loadData(tabContext.props.name);
};

// 2. 删除视频逻辑
const handleDelete = (id) => {
  ElMessageBox.confirm('确定删除该视频吗？此操作不可恢复', '警告', { 
    type: 'warning',
    confirmButtonText: '确定删除',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await deleteVideo(id);
      ElMessage.success('删除成功');
      loadData(); // 刷新列表
    } catch (error) {
      ElMessage.error('删除失败');
    }
  });
};

// 3. 头像上传逻辑
const triggerFileInput = () => {
  fileInput.value.click(); // 触发隐藏的 input 点击事件
};

const handleAvatarUpload = async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await uploadAvatar(formData);
    if (res.data.code === 200) {
      // 成功后，更新预览图
      editForm.value.avatar = res.data.url;
      ElMessage.success('图片上传成功，请记得点击下方"保存所有修改"');
    } else {
      ElMessage.error(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    ElMessage.error('头像上传失败');
  }
};

// 4. 保存资料逻辑
const handleUpdateProfile = async () => {
  try {
    const res = await updateProfile({
      user_id: userStore.userInfo.id,
      ...editForm.value
    });
    if (res.data.code === 200) {
      ElMessage.success('资料修改成功');
      // 更新 Pinia 和 LocalStorage
      userStore.setLoginState(userStore.token, res.data.data);
      // 更新当前页面显示的头部信息
      userInfo.value = res.data.data;
      // 清空密码框防止重复提交
      editForm.value.password = '';
    } else {
      ElMessage.error(res.data.msg);
    }
  } catch (error) {
    ElMessage.error('修改失败');
  }
};

// 初始化
onMounted(() => loadData());
</script>

<style scoped>
.profile-container { 
  max-width: 900px; 
  margin: 20px auto; 
  padding: 0 10px;
}
.user-header { 
  display: flex; 
  align-items: center; 
  margin-bottom: 30px; 
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}
.info { 
  margin-left: 20px; 
}
.info h2 {
  margin: 0 0 10px 0;
  color: #333;
}

/* 视频列表网格 */
.video-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); 
  gap: 20px; 
}
.cover { 
  width: 100%; 
  height: 120px; 
  object-fit: cover; 
}
.video-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
}

/* 头像上传组件样式 */
.avatar-uploader {
  width: 100px;
  height: 100px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  display: flex;
  justify-content: center;
  align-items: center;
}
.avatar-uploader:hover {
  border-color: #409EFF;
}
.avatar-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}
/* 遮罩层 - 只有鼠标悬停时才显示稍微明显一点，或者常驻在底部 */
.upload-mask {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: rgba(0,0,0,0.6);
  color: white;
  font-size: 12px;
  text-align: center;
  line-height: 24px;
  opacity: 0.8;
  transition: opacity 0.3s;
}
.avatar-uploader:hover .upload-mask {
  opacity: 1;
}
</style>