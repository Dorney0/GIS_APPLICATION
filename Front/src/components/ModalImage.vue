<template>
  <div v-if="visible" class="modal-backdrop" @click.self="close">
    <div class="modal-content">
      <button class="close-btn" @click="close">×</button>
      <img :src="imageSrc" alt="Фрагмент" class="modal-image" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean,
  imageSrc: String
});
const emit = defineEmits(["close"]);
function close() {
  emit("close");
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  background-color: white;
  padding: 10px;
  border-radius: 8px;
  max-width: 90%;
  max-height: 90%;
  overflow: auto;
}

.modal-image {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 4px;
}

.close-btn {
  position: absolute;
  top: 6px;
  right: 10px;
  font-size: 22px;
  background: none;
  border: none;
  cursor: pointer;
  color: red;
}

</style>
