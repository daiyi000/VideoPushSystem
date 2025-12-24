<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>视频内容管理</span>
        <div class="header-actions">
          <el-select 
            v-model="filterStatus" 
            placeholder="状态筛选" 
            @change="loadData" 
            size="small" 
            style="width: 120px"
          >
            <el-option label="全部状态" value="" />
            <el-option label="待审核" value="0" />
            <el-option label="已发布" value="1" />
            <el-option label="已下架" value="2" />
          </el-select>
        </div>
      </div>
    </template>

    <el-table :data="tableData" style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="封面" width="100">
        <template #default="scope">
          <div class="video-cover-wrapper">
            <img :src="scope.row.cover_url" class="video-cover">
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" show-overflow-tooltip min-width="200" />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.status===0" type="warning" effect="plain" round>待审核</el-tag>
          <el-tag v-else-if="scope.row.status===1" type="success" effect="plain" round>正常</el-tag>
          <el-tag v-else type="danger" effect="plain" round>已下架</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" align="right">
        <template #default="scope">
          <div class="action-links">
            <!-- 1. 审核 -->
            <el-button 
              v-if="scope.row.status === 0 || scope.row.status === 2" 
              link type="primary" 
              @click="goToAudit(scope.row.id)"
            >
              审核
            </el-button>

            <!-- 2. 下架 -->
            <el-button 
              v-if="scope.row.status === 1" 
              link type="warning" 
              @click="handleAudit(scope.row, 2)"
            >
              下架
            </el-button>
            
            <!-- 3. 预览 -->
            <el-button 
              v-if="scope.row.status === 1"
              link type="primary"
              @click="openPreview(scope.row)"
            >
              预览
            </el-button>

            <!-- 4. 删�� -->
            <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </div>
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
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.video-cover-wrapper {
  width: 80px;
  height: 45px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #eee;
}

.video-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.action-links .el-button {
  margin-left: 0;
  margin-right: 12px;
  font-size: 13px;
}
</style>