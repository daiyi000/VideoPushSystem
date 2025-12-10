<template>
  <div class="filter-bar-container">
    <div class="tags-wrapper">
      <div 
        v-for="cat in categories" 
        :key="cat"
        :class="['tag-pill', { active: modelValue === cat }]"
        @click="$emit('update:modelValue', cat); $emit('change', cat)"
      >
        {{ cat }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  categories: { type: Array, required: true },
  modelValue: { type: String, required: true }
});
defineEmits(['update:modelValue', 'change']);
</script>

<style scoped>
.filter-bar-container {
  /* 【核心修改】吸顶且背景透明 */
  position: sticky;
  top: 0; 
  z-index: 10;
  background: rgba(255, 255, 255, 0.98); /* 极高不透明度的白 */
  backdrop-filter: blur(2px);
  padding: 12px 24px;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
}

.tags-wrapper {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  width: 100%;
  scrollbar-width: none; 
}
.tags-wrapper::-webkit-scrollbar { display: none; }

.tag-pill {
  padding: 6px 12px;
  background: rgba(0,0,0,0.05);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  color: #0f0f0f;
  user-select: none;
}
.tag-pill:hover { background: #e5e5e5; }
.tag-pill.active { background: #0f0f0f; color: white; }
</style>