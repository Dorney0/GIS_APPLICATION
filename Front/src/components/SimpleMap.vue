<template>
  <div id="map" class="map"></div>
</template>

<script setup>
import { onMounted } from 'vue'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import OSM from 'ol/source/OSM'

import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import GeoJSON from 'ol/format/GeoJSON'
import { Fill, Stroke, Style } from 'ol/style'
import { fromLonLat } from 'ol/proj'

onMounted(async () => {
  const response = await fetch('http://localhost:5269/api/geoimages/geojson')
  const geojsonData = await response.json()

  const vectorSource = new VectorSource({
    features: new GeoJSON().readFeatures(geojsonData, {
      dataProjection: 'EPSG:4326',
      featureProjection: 'EPSG:3857',
    }),
  })

  const vectorLayer = new VectorLayer({
    source: vectorSource,
    style: new Style({
      stroke: new Stroke({
        color: 'red',
        width: 2,
      }),
      fill: new Fill({
        color: 'rgba(255, 0, 0, 0.2)',
      }),
    }),
  })

  const map = new Map({
    target: 'map',
    layers: [
      new TileLayer({
        source: new OSM(),
      }),
      vectorLayer,
    ],
    view: new View({
      center: fromLonLat([137, 58]),
      zoom: 5,
    }),
  })

  map.getView().fit(vectorSource.getExtent(), {
    padding: [20, 20, 20, 20],
    maxZoom: 10,
  })
})
</script>

<style>
html, body, #app, #map {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}
.map {
  width: 100%;
  height: 100vh;
}
</style>
