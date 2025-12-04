<template>
  <el-card>
    <div class="header">
      <h2>视频内容管理</h2>
      <el-select v-model="filterStatus" placeholder="状态筛选" @change="loadData">
        <el-option label="全部" value="" />
        <el-option label="待审核" value="0" />
        <el-option label="已发布" value="1" />
        <el-option label="已下架" value="2" />
      </el-select>
    </div>

    <el-table :data="tableData" style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="封面" width="120">
        <template #default="scope">
          <img :src="scope.row.cover_url" style="width: 100px; height: 60px; object-fit: cover; border-radius: 4px;">
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" show-overflow-tooltip />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.status===0" type="warning">待审核</el-tag>
          <el-tag v-else-if="scope.row.status===1" type="success">正常</el-tag>
          <el-tag v-else type="danger">已下架</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280">
        <template #default="scope">
          
          <!-- 1. 审核按钮 (待审核 或 已下架 显示去审核) -->
          <el-button 
            v-if="scope.row.status === 0 || scope.row.status === 2" 
            size="small" 
            type="primary" 
            @click="goToAudit(scope.row.id)"
          >
            去审核
          </el-button>

          <!-- 2. 下架按钮 (仅正常状态显示) -->
          <el-button 
            v-if="scope.row.status === 1" 
            size="small" 
            type="warning" 
            @click="handleAudit(scope.row, 2)"
          >
            下架
          </el-button>
          
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          
          <!-- 4. 预览 (仅已发布状态显示) -->
          <el-button 
            v-if="scope.row.status === 1"
            size="small" 
            @click="openPreview(scope.row)"
          >
            预览
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getAdminVideos, auditVideo, deleteVideoAdmin } from '../../api/admin';
import { ElMessage, ElMessageBox } from 'element-plus';

const router = useRouter();
const tableData = ref([]);
const filterStatus = ref('');

const loadData = async () => {
  const res = await getAdminVideos({ status: filterStatus.value });
  tableData.value = res.data.data;
};

// 快捷操作 (直接在列表页改状态)
const handleAudit = async (row, status) => {
  await auditVideo({ id: row.id, status });
  ElMessage.success('操作成功');
  loadData();
};

const handleDelete = (row) => {
  ElMessageBox.confirm('确定彻底删除该视频？', '警告', { type: 'warning' }).then(async () => {
    await deleteVideoAdmin(row.id);
    ElMessage.success('删除成功');
    loadData();
  });
};

// 跳转到专用审核页
const goToAudit = (id) => {
  router.push(`/admin/audit/${id}`);
};

// 在新标签页预览 (前台逻辑)
const openPreview = (row) => {
  const url = router.resolve({ path: `/video/${row.id}` }).href;
  window.open(url, '_blank');
};

onMounted(() => loadData());
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
</style>