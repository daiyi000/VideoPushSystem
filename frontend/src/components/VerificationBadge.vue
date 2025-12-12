<template>
  <el-tooltip v-if="type > 0" :content="typeName" placement="top">
    <div class="badge-wrapper">
      
      <img 
        v-if="type === 1" 
        :src="verifiedIcon" 
        class="custom-badge" 
        alt="个人认证"
      />
      
      <img 
        v-if="type === 2" 
        :src="musicIcon" 
        class="custom-badge" 
        alt="音乐人认证"
      />
      
    </div>
  </el-tooltip>
</template>

<script setup>
import { computed } from 'vue';

// 【关键步骤】引入你的 SVG 文件
// @ 符号在 Vite 中通常指向 src 目录
import verifiedIcon from '@/assets/icons/verified.svg';
import musicIcon from '@/assets/icons/music.svg';

const props = defineProps({
  type: { type: Number, default: 0 }
});

const typeName = computed(() => props.type === 1 ? '认证用户' : '认证音乐人');
</script>

<style scoped>
.badge-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 4px;
  vertical-align: middle;
  /* 调整这里可以微调图标的垂直位置 */
  transform: translateY(-1px); 
}

.custom-badge {
  /* 【关键】控制 SVG 的大小 */
  width: 16px; 
  height: 16px;
  
  /* 保持图片比例 */
  object-fit: contain; 
  
  /* 这是一个可选属性，确保图片不被选中变蓝 */
  user-select: none;
  -webkit-user-drag: none;
}
</style>