import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

import { features, selectedFeatures } from './store.js'

router.beforeEach((to, from, next) => {
    to.meta.features = features.value
    to.meta.selectedFeatures = selectedFeatures.value
    next()
})

createApp(App).use(router).mount('#app')
