<template>
  <div class="app-container">
    <MapWithTable
        :features="features"
        :selectedFeatures="selectedFeatures"
        @update:selectedFeatures="val => selectedFeatures = val"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MapWithTable from './components/MapWithTable.vue'

const features = ref([])
const selectedFeatures = ref([])

onMounted(async () => {
  const res = await fetch('http://localhost:5269/api/geoimages/geojson')
  const geojson = await res.json()
  console.log('features из API:', geojson.features)
  console.log('Количество фич:', geojson.features.length)
  features.value = geojson.features
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  overflow: hidden;
}
</style>
