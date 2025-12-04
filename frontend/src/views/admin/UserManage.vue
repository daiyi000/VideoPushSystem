<template>
  <el-card>
    <h2>用户管理</h2>
    <el-table :data="tableData">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="头像" width="70">
        <template #default="scope">
          <el-avatar :src="scope.row.avatar" />
        </template>
      </el-table-column>
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.is_banned" type="danger">封禁中</el-tag>
          <el-tag v-else type="success">正常</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button 
            :type="scope.row.is_banned ? 'success' : 'danger'" 
            size="small" 
            @click="handleBan(scope.row)"
            :disabled="scope.row.is_admin" 
          >
            {{ scope.row.is_banned ? '解封' : '封禁' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getAdminUsers, banUser } from '../../api/admin';
import { ElMessage } from 'element-plus';

const tableData = ref([]);

const loadData = async () => {
  const res = await getAdminUsers();
  tableData.value = res.data.data;
};

const handleBan = async (row) => {
  const res = await banUser(row.id);
  ElMessage.success(res.data.msg);
  loadData();
};

onMounted(() => loadData());
</script>