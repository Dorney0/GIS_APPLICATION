<template>
  <div class="table-top">
    <h2>Таблица фрагментов</h2>
    <div class="table-wrapper" ref="tableWrapperRef">
      <table>
        <thead>
        <tr>
          <th>Выбрать</th>
          <th>Product ID</th>
          <th>Entity ID</th>
          <th>Тип</th>
          <th>PR</th>
        </tr>
        </thead>
        <tbody>
        <tr
            v-for="(feature, index) in features"
            :key="feature.properties.entityid"
            :ref="el => { if(el) rowRefs[feature.properties.entityid] = el }"
            :class="{ hovered: feature.properties.entityid === hoveredFeatureId }"
            @click="$emit('rowClicked', feature)"
        >
          <td>
            <input
                type="checkbox"
                v-model="localSelected"
                :value="feature.properties.entityid"
                @click.stop
            />
          </td>
          <td>{{ feature.properties.productid }}</td>
          <td>{{ feature.properties.entityid }}</td>
          <td>{{ feature.properties.tipo }}</td>
          <td>{{ feature.properties.pr }}</td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, toRaw, nextTick } from 'vue'
import { reactive } from 'vue'

const rowRefs = reactive({})

const props = defineProps({
  features: Array,
  selectedFeatures: Array,
  hoveredFeatureId: String,
})

const emit = defineEmits(['update:selectedFeatures', 'rowClicked'])

const localSelected = ref([...props.selectedFeatures])

const tableWrapperRef = ref(null)

watch(
    () => props.hoveredFeatureId,
    async (hoveredId) => {
      await nextTick()
      if (hoveredId && tableWrapperRef.value) {
        const rowEl = rowRefs[hoveredId]
        const wrapper = tableWrapperRef.value
        if (rowEl) {
          const rowRect = rowEl.getBoundingClientRect()
          const wrapperRect = wrapper.getBoundingClientRect()

          const rowHeight = rowRect.height
          const extraOffset = 7 // Дополнительные

          // scrollTop прокручиваем к offsetTop минус высота строки и 4 пикселя
          const offset = rowEl.offsetTop - rowHeight - extraOffset

          wrapper.scrollTo({
            top: offset,
            behavior: 'smooth'
          })
        }
      }
    }
)




watch(localSelected, (val) => {
  const rawVal = toRaw(val)
  const rawSelected = toRaw(props.selectedFeatures)
  if (JSON.stringify(rawVal) !== JSON.stringify(rawSelected)) {
    emit('update:selectedFeatures', rawVal)
  }
})
</script>


<style scoped>
.table-top {
  height: 100%;
  padding: 15px;
}

.table-wrapper {
  height: 100%;
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #ddd;
}

table {
  font-size: 0.8rem;
  width: 100%;
  table-layout: fixed;
}

thead th {
  position: sticky;
  top: 0;
  background-color: #f1f1f1;
  z-index: 10;
  padding: 0.6rem 0.9rem;
  border: 1px solid #ddd;
  text-align: left;
}

tbody tr:hover {
  cursor: pointer;
  background-color: #f5f5f5;
}

.hovered {
  background-color: #ffebee !important;
}

th, td {
  padding: 0.3rem 0.5rem;
  border: 1px solid #ddd;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: left;
}
.table-top h2 {
  margin: 5px;
  padding: 0;
  font-size: 1rem;
  line-height: 1;
  font-weight: 600;
}

</style>
