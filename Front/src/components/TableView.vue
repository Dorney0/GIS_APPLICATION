<template>
  <div class="table-container">
    <h2>Таблица фрагментов</h2>
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
      <tr v-for="(feature, index) in features" :key="index">
        <td>
          <input
              type="checkbox"
              :value="feature.properties.entityid"
              :checked="localSelected.includes(feature.properties.entityid)"
              @change="toggleSelection(feature.properties.entityid)"
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
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  features: Array,
  selectedFeatures: Array
})
const emit = defineEmits(['update:selectedFeatures'])

const localSelected = ref([...props.selectedFeatures])

watch(() => props.selectedFeatures, (val) => {
  localSelected.value = [...val]
})

function toggleSelection(id) {
  const index = localSelected.value.indexOf(id)
  if (index === -1) {
    localSelected.value.push(id)
  } else {
    localSelected.value.splice(index, 1)
  }

  emit('update:selectedFeatures', [...localSelected.value])
}
</script>

<style scoped>
.table-container {
  padding: 2rem;
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}
th, td {
  padding: 0.6rem 0.9rem;
  border: 1px solid #ddd;
}
th {
  background-color: #f1f1f1;
  text-align: left;
}
</style>
