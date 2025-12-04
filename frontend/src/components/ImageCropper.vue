<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="600px"
    :close-on-click-modal="false"
    @closed="handleClosed"
    append-to-body
  >
    <div class="cropper-container" v-if="imageUrl">
      <img ref="imageRef" :src="imageUrl" style="max-width: 100%; display: block;" />
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="loading">确认上传</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, nextTick, shallowRef } from 'vue';
import Cropper from 'cropperjs';
import 'cropperjs/dist/cropper.css'; 

const props = defineProps({
  title: { type: String, default: '图片裁剪' },
  aspectRatio: { type: Number, default: 1 }, 
});

const emit = defineEmits(['upload']);

const visible = ref(false);
const imageUrl = ref('');
const imageRef = ref(null);
const cropperInstance = shallowRef(null);
const loading = ref(false);

const open = (file) => {
  const reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onload = (e) => {
    imageUrl.value = e.target.result;
    visible.value = true;
    
    nextTick(() => {
      if (cropperInstance.value) {
        cropperInstance.value.destroy();
      }
      // 初始化本地 Cropper
      if (imageRef.value) {
        cropperInstance.value = new Cropper(imageRef.value, {
          aspectRatio: props.aspectRatio,
          viewMode: 1,
          autoCropArea: 1,
        });
      }
    });
  };
};

const handleConfirm = () => {
  if (!cropperInstance.value) {
    return;
  }
  
  loading.value = true;
  
  try {
      const canvas = cropperInstance.value.getCroppedCanvas();
      
      if (!canvas) {
          loading.value = false;
          return; 
      }
      
      canvas.toBlob((blob) => {
        if (!blob) {
             loading.value = false;
             return;
        }
        emit('upload', blob, () => {
          loading.value = false;
          visible.value = false;
        });
      }, 'image/jpeg', 0.8);
  } catch (error) {
      console.error("裁剪错误:", error);
      loading.value = false;
  }
};

const handleClosed = () => {
  if (cropperInstance.value) {
    cropperInstance.value.destroy();
    cropperInstance.value = null;
  }
  imageUrl.value = '';
};

defineExpose({ open });
</script>

<style scoped>
.cropper-container {
  height: 400px;
  width: 100%;
  background: #f0f0f0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
img {
  max-width: 100%;
  display: block;
}
</style>