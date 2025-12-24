<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <!-- Apple Style Segmented Control -->
        <div class="segmented-control">
          <div 
            class="segment-item" 
            :class="{ active: viewMode === 'users' }"
            @click="switchMode('users')"
          >
            Users
          </div>
          <div 
            class="segment-item" 
            :class="{ active: viewMode === 'requests' }"
            @click="switchMode('requests')"
          >
            Reset Requests
          </div>
        </div>

        <el-input 
          v-if="viewMode === 'users'"
          v-model="searchQuery" 
          placeholder="搜索用户" 
          prefix-icon="Search" 
          class="apple-search" 
          clearable 
        />
      </div>
    </template>
    
    <!-- User List Table -->
    <el-table v-if="viewMode === 'users'" :data="filteredData">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column label="头像" width="80">
        <template #default="scope">
          <el-avatar :src="scope.row.avatar" :size="36" />
        </template>
      </el-table-column>
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.is_banned" type="danger" effect="plain" round>封禁中</el-tag>
          <el-tag v-else type="success" effect="plain" round>正常</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" align="right">
        <template #default="scope">
          <el-button 
            v-if="!scope.row.is_admin"
            type="primary" 
            link
            @click="handleBan(scope.row)"
          >
            {{ scope.row.is_banned ? '解封' : '封禁' }}
          </el-button>
          <span v-else style="color:#999; font-size:12px">管理员</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- Reset Requests Table -->
    <el-table v-else :data="requestsData">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="email" label="邮箱" min-width="200" />
      <el-table-column prop="created_at" label="申请时间" width="180" />
      <el-table-column label="状态" width="120">
        <template #default="scope">
          <el-tag v-if="scope.row.status === 'pending'" type="warning" effect="plain" round>待处理</el-tag>
          <el-tag v-else-if="scope.row.status === 'sent'" type="success" effect="plain" round>已发送</el-tag>
          <el-tag v-else type="info" effect="plain" round>已完成</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="right">
        <template #default="scope">
          <el-button 
            v-if="scope.row.status === 'pending'"
            type="primary" 
            link
            @click="handleSendEmail(scope.row)"
            :loading="emailLoading === scope.row.id"
          >
            发送重置邮件
          </el-button>
          <span v-else style="color:#999; font-size:12px">--</span>
        </template>
      </el-table-column>
    </el-table>

  </el-card>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getAdminUsers, banUser, getResetRequests, sendResetEmail } from '../../api/admin';
import { ElMessage } from 'element-plus';
import { Search } from '@element-plus/icons-vue';

const viewMode = ref('users'); // 'users' or 'requests'
const tableData = ref([]);
const requestsData = ref([]);
const searchQuery = ref('');
const emailLoading = ref(null);

const loadUsers = async () => {
  const res = await getAdminUsers();
  tableData.value = res.data.data;
};

const loadRequests = async () => {
  const res = await getResetRequests();
  requestsData.value = res.data.data;
};

const switchMode = (mode) => {
  viewMode.value = mode;
  if (mode === 'users') loadUsers();
  else loadRequests();
};

const filteredData = computed(() => {
  if (!searchQuery.value) return tableData.value;
  const q = searchQuery.value.toLowerCase();
  return tableData.value.filter(u => 
    u.username.toLowerCase().includes(q) || 
    (u.email && u.email.toLowerCase().includes(q))
  );
});

const handleBan = async (row) => {
  const res = await banUser(row.id);
  ElMessage.success(res.data.msg);
  loadUsers();
};

const handleSendEmail = async (row) => {
  emailLoading.value = row.id;
  try {
    const res = await sendResetEmail(row.id);
    if (res.data.code === 200) {
      ElMessage.success('邮件已发送');
      loadRequests();
    } else {
      ElMessage.error(res.data.msg);
    }
  } catch (e) {
    ElMessage.error('发送失败');
  } finally {
    emailLoading.value = null;
  }
};

onMounted(() => loadUsers());
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Apple Style Segmented Control */
.segmented-control {
  background: #E5E5EA;
  padding: 2px;
  border-radius: 8px;
  display: flex;
  width: fit-content;
}

.segment-item {
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 6px;
  color: #636366;
  transition: all 0.2s ease;
}

.segment-item.active {
  background: #FFFFFF;
  color: #000;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.apple-search {
  width: 200px;
}

:deep(.apple-search .el-input__wrapper) {
  border-radius: 99px;
  background-color: #F5F5F7;
  box-shadow: none !important;
}
</style>