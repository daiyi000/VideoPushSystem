<template>
  <div class="filter-bar-container">
    <div class="filter-scroll">
      <div 
        v-for="cat in categories" 
        :key="cat" 
        class="filter-chip"
        :class="{ active: modelValue === cat }"
        @click="handleClick(cat)"
      >
        {{ cat }}
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  modelValue: {
    type: String,
    default: '全部'
  }
});

const emit = defineEmits(['update:modelValue', 'change']);

const handleClick = (cat) => {
  if (cat === props.modelValue && cat !== '全部') {
    emit('update:modelValue', '全部');
    emit('change', '全部');
  } else {
    emit('update:modelValue', cat);
    emit('change', cat);
  }
};
</script>

<style scoped>
.filter-bar-container {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 24px;
  border-bottom: 1px solid #e5e5e5;
  width: 100%;
}

.filter-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  scrollbar-width: none; 
}
.filter-scroll::-webkit-scrollbar { display: none; }

.filter-chip {
  padding: 6px 12px;
  background: #f2f2f2;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #0f0f0f;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  user-select: none;
}

.filter-chip:hover {
  background: #e5e5e5;
}

.filter-chip.active {
  background: #0f0f0f;
  color: #fff;
}
</style>