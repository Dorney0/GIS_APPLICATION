<template>
  <div class="app-container">
    <Sidebar />
    <div class="main-content">
      <router-view
          :features="features"
          :selectedFeatures="selectedFeatures"
          @update:selectedFeatures="val => selectedFeatures = val"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'

const features = ref([])
const selectedFeatures = ref([])

onMounted(async () => {
  const res = await fetch('http://localhost:5269/api/geoimages/geojson')
  const geojson = await res.json()
  features.value = geojson.features
})
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.main-content {
  flex-grow: 1;
  overflow: auto;
}
</style>
