<template>
  <component
      :is="routeComponent"
      :features="features"
      :selectedFeatures="selectedFeatures"
      @update:selectedFeatures="$emit('update:selectedFeatures', $event)"
  />
</template>

<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const props = defineProps({
  features: Array,
  selectedFeatures: Array
})
const emit = defineEmits(['update:selectedFeatures'])

const route = useRoute()

const routeComponent = computed(() => route.matched[route.matched.length - 1]?.components?.default)
</script>
