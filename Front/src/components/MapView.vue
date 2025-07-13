<template>
  <div style="position: relative; height: 100%;">
    <div id="map" class="map"></div>
    <div style="position: absolute; top: 20px; right: 50px; background: white; padding: 6px; border-radius: 4px; box-shadow: 0 0 5px rgba(0,0,0,0.3); z-index: 1000;">
      <label>
        <input type="checkbox" v-model="showLabels" />
        Показать надписи
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import OSM from 'ol/source/OSM'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import GeoJSON from 'ol/format/GeoJSON'
import { Fill, Stroke, Style, Text } from 'ol/style'
import { fromLonLat } from 'ol/proj'

const props = defineProps({
  features: Array,
  selectedFeatures: Array
})

const showLabels = ref(true)  // управление показом надписей

const redStyle = (feature) => {
  const productid = feature.get('productid') || ''
  const rawDate = productid.substring(17, 25) || ''  // "20220502"

  let dateText = 'нет даты'
  if (rawDate.length === 8) {
    const year = rawDate.substring(0, 4)
    const month = rawDate.substring(4, 6)
    const day = rawDate.substring(6, 8)
    dateText = `Дата: ${day}-${month}-${year}`
  }

  return new Style({
    stroke: new Stroke({color: 'red', width: 2}),
    fill: new Fill({color: 'rgba(255, 0, 0, 0.2)'}),
    text: showLabels.value ? new Text({
      text: dateText,
      fill: new Fill({color: 'black'}),
      stroke: new Stroke({color: 'white', width: 2}),
      font: '25px Calibri,sans-serif',
      overflow: true,
    }) : null,
  })
}

const hiddenStyle = new Style({
  stroke: new Stroke({color: 'rgba(0, 0, 0, 0)', width: 0}),
  fill: new Fill({color: 'rgba(0, 0, 0, 0)'}),
  text: null,
})

const vectorSource = new VectorSource()
let map

function updateFeatures() {
  vectorSource.clear()

  if (props.features?.length > 0) {
    const olFeatures = new GeoJSON().readFeatures({
      type: 'FeatureCollection',
      features: props.features
    }, {
      dataProjection: 'EPSG:4326',
      featureProjection: 'EPSG:3857'
    })

    olFeatures.forEach(f => {
      const entityid = f.getProperties()?.entityid || f.get('entityid')
      f.setId(entityid)
      f.setStyle(hiddenStyle) // Изначально все скрыты
      vectorSource.addFeature(f)
    })

    if (!vectorSource.isEmpty()) {
      map.getView().fit(vectorSource.getExtent(), {
        padding: [20, 20, 20, 20],
        maxZoom: 10
      })
    }
  }
}

function updateStyles() {
  const selected = props.selectedFeatures.map(String)
  vectorSource.getFeatures().forEach(f => {
    const id = String(f.getId())
    if (selected.includes(id)) {
      f.setStyle(redStyle(f))
    } else {
      f.setStyle(hiddenStyle)
    }
  })
}

onMounted(() => {
  const tileLayer = new TileLayer({source: new OSM()})
  const vectorLayer = new VectorLayer({source: vectorSource})

  map = new Map({
    target: 'map',
    layers: [tileLayer, vectorLayer],
    view: new View({
      center: fromLonLat([137, 58]),
      zoom: 5
    })
  })

  updateFeatures()
  updateStyles()
})

// Реагируем на изменения пропсов и локального флага showLabels
watch(() => props.features, () => {
  updateFeatures()
  updateStyles()
}, {deep: true})

watch(() => props.selectedFeatures, () => {
  updateStyles()
}, {deep: true})

watch(showLabels, () => {
  updateStyles()
})
</script>

<style scoped>
.map {
  width: 100%;
  height: 100%;
}
</style>
