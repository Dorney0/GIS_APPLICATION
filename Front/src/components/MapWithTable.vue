<template>
  <div class="map-with-table">
    <div class="map-container">
    <MapView
        :features="features"
        :selectedFeatures="selectedFeatures"
        @update:selectedFeatures="$emit('update:selectedFeatures', $event)"
        @hoverFeature="hoveredFeatureId = $event"
      />
      <button
          class="toggle-button"
          :style="{ bottom: tableVisible ? '5px' : '35px' }"
          @click="tableVisible = !tableVisible"
      >
        {{ tableVisible ? 'Скрыть таблицу' : 'Показать таблицу' }}
      </button>

    </div>
    <Modal
        v-if="selectedFeatureForModal"
        :feature="selectedFeatureForModal"
        @close="closeModal"
    />
    <transition name="slide-up">
      <div v-show="tableVisible" class="table-container">
        <TableView
            :hoveredFeatureId="hoveredFeatureId"
            :features="features"
            :selectedFeatures="selectedFeatures"
            @update:selectedFeatures="$emit('update:selectedFeatures', $event)"
            @rowClicked="openModal"
        />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MapView from './MapView.vue'
import TableView from './TableView.vue'
import Modal from './Modal.vue'
const hoveredFeatureId = ref(null)
const selectedFeatureForModal = ref(null)

function openModal(feature) {
  selectedFeatureForModal.value = feature
}

function closeModal() {
  selectedFeatureForModal.value = null
}
const props = defineProps({
  features: {
    type: Array,
    default: () => []
  },
  selectedFeatures: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:selectedFeatures'])

const tableVisible = ref(true)

</script>

<style scoped>
.map-with-table {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.map-container {
  flex: 1;
  position: relative;
}

.table-container {
  padding-bottom: 50px;
  height: 250px;
  border-top: 1px solid #ccc;
  background-color: #fff;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}

/* Кнопка поверх карты, в левом нижнем углу */
.toggle-button {
  position: absolute;
  bottom: 35px;
  left: 16px;
  z-index: 1000;
  padding: 6px 12px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  transition: background-color 0.3s;
}

.toggle-button:hover {
  background-color: #1565c0;
}

/* Анимация появления/исчезновения таблицы */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: max-height 0.6s ease, opacity 0.6s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
}
.slide-up-enter-to,
.slide-up-leave-from {
  max-height: 400px;
  opacity: 1;
}
</style>
