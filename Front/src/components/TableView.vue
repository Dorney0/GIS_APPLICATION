<template>
  <div class="table-top">
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
      <tr v-for="(feature, index) in features" :key="feature.properties.entityid">
        <td>
          <input
              type="checkbox"
              v-model="localSelected"
              :value="feature.properties.entityid"
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
import { ref, watch, toRaw } from 'vue'

const props = defineProps({
  features: Array,
  selectedFeatures: Array
})

const emit = defineEmits(['update:selectedFeatures'])

const localSelected = ref([...props.selectedFeatures])

watch(() => props.selectedFeatures, val => {
  localSelected.value = [...val]
})

// Проверяем и эмитим только при реальном изменении
watch(localSelected, val => {
  const rawVal = toRaw(val)
  const rawSelected = toRaw(props.selectedFeatures)

  if (JSON.stringify(rawVal) !== JSON.stringify(rawSelected)) {
    emit('update:selectedFeatures', rawVal)
  }
})
</script>

<style scoped>
.table-top {
  padding: 15px;
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
