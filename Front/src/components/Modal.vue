<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal">
      <h3>Действия с фрагментом</h3>
      <p><strong>Entity ID:</strong> {{ feature?.properties.entityid }}</p>
      <p><strong>Product ID:</strong> {{ feature?.properties.productid }}</p>
      <div class="actions">
        <button @click="combineBands">Объединить слои (7 6 2)</button>
        <button @click="generateMask">Сформировать маску</button>
        <button @click="detectFire">Обнаружить пожар</button>
      </div>
      <button class="close" @click="$emit('close')">Закрыть</button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  feature: Object
})

const emit = defineEmits(['close'])

function generateMask() {
  alert('Маска сформирована для ' + props.feature?.properties.entityid)
}

function detectFire() {
  alert('Пожар обнаружен для ' + props.feature?.properties.entityid)
}

function combineBands() {
  alert('Слои 7, 6, 2 объединены для ' + props.feature?.properties.entityid)
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0; left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}
.modal {
  background: white;
  padding: 20px 30px;
  border-radius: 8px;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 15px 0;
}
button {
  padding: 6px 12px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background-color: #1565c0;
}
.close {
  background: #aaa;
}
.close:hover {
  background-color: #d32f2f; /* красный */
  color: white;
}

</style>
