<template>
  <div style="position: relative; height: 100%;">
    <div id="map" class="map"></div>

    <div style="position: absolute; top: 20px; right: 50px; background: white; padding: 10px; border-radius: 4px; box-shadow: 0 0 5px rgba(0,0,0,0.3); z-index: 1000;">
      <div style="margin-bottom: 8px;">
        <button
            class="upload-button"
            style="margin-bottom: 10px;"
            @click="triggerFolderSelect"
        >
          Загрузить изображения
        </button>
        <input
            ref="folderInput"
            type="file"
            style="display: none;"
            webkitdirectory
            @change="handleFolderSelect"
        />

      </div>

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

const emit = defineEmits(['hoverFeature'])
const showLabels = ref(true)  // флаг для показа текста

// Базовый стиль для всех фич (серый, прозрачный фон)
const baseStyle = new Style({
  stroke: new Stroke({ color: 'rgba(0, 0, 0, 0)', width: 0 }),
  fill: new Fill({ color: 'rgba(0, 0, 0, 0)' }),
  text: null,
})

// Стиль с красным выделением и текстом даты
const styleWithText = (feature) => {
  const productid = feature.get('productid') || ''
  const rawDate = productid.substring(17, 25) || ''

  let dateText = 'нет даты'
  if (rawDate.length === 8) {
    const year = rawDate.substring(0, 4)
    const month = rawDate.substring(4, 6)
    const day = rawDate.substring(6, 8)
    dateText = `Дата: ${day}-${month}-${year}`
  }

  return new Style({
    stroke: new Stroke({ color: 'red', width: 2 }),
    fill: new Fill({ color: 'rgba(255, 0, 0, 0.2)' }),
    text: showLabels.value ? new Text({
      text: dateText,
      fill: new Fill({ color: 'black' }),
      stroke: new Stroke({ color: 'white', width: 2 }),
      font: '16px Calibri,sans-serif',
      overflow: true,
    }) : null,
  })
}

const vectorSource = new VectorSource()
let map

const folderInput = ref(null)

function triggerFolderSelect() {
  folderInput.value?.click()
}

async function handleFolderSelect(event) {
  const files = event.target.files
  if (!files || files.length === 0) {
    console.warn('⚠️ Нет выбранных файлов')
    return
  }

  const formData = new FormData()

  for (const file of files) {
    console.log('📦 Добавлен файл:', file.name)
    formData.append('files', file)
  }

  try {
    console.log('⏳ Отправка данных на сервер...')
    const res = await fetch('http://localhost:5269/api/ImageUpload/upload', {
      method: 'POST',
      body: formData
    })

    if (!res.ok) throw new Error(`Ошибка: ${res.status}`)

    const result = await res.json()
    console.log('✅ Успешная загрузка:', result)
    alert('Файлы успешно загружены')
  } catch (err) {
    console.error('❌ Ошибка при загрузке файлов:', err);
    alert('Ошибка загрузки файлов');
  }

  // сброс input, чтобы можно было повторно выбрать ту же папку
  event.target.value = null
}

function updateFeatures() {
  console.log('🔄 Обновляем features:', props.features?.length)
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
      f.setStyle(baseStyle) // базовый стиль по умолчанию
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
      f.setStyle(styleWithText(f))  // красный стиль с текстом
    } else {
      f.setStyle(baseStyle)  // базовый серый стиль
    }
  })
}

onMounted(() => {
  const tileLayer = new TileLayer({
    source: new OSM({
      attributions: []
    })
  });

  const vectorLayer = new VectorLayer({
    source: vectorSource,
    declutter: true, // помогает убрать пересекающиеся текстовые метки
  })

  map = new Map({
    target: 'map',
    layers: [tileLayer, vectorLayer],
    view: new View({
      center: fromLonLat([137, 58]),
      zoom: 5
    })
  })

  map.on('pointermove', function (evt) {
    const pixel = map.getEventPixel(evt.originalEvent)
    const feature = map.forEachFeatureAtPixel(pixel, f => {
      // Проверим, есть ли стиль, который визуально отображает объект
      const style = f.getStyle()
      return style && (style.getStroke()?.getColor() !== 'rgba(0, 0, 0, 0)' || style.getFill()?.getColor() !== 'rgba(0, 0, 0, 0)')
          ? f
          : null
    })

    if (feature && props.selectedFeatures.includes(feature.getId())) {
      emit('hoverFeature', feature.getId())
    } else {
      emit('hoverFeature', null)
    }
  })

  updateFeatures()
  updateStyles()
})

// Следим за изменениями входных данных и флага showLabels
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
.upload-button {
  padding: 6px 12px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  transition: background-color 0.3s;
}
.upload-button:hover {
  background-color: #1565c0;
}

.map {
  width: 100%;
  height: 100%;
}

</style>
