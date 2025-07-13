import { createRouter, createWebHistory } from 'vue-router'
import MapView from '../components/MapView.vue'
import TableView from '../components/TableView.vue'

const routes = [
    {
        path: '/',
        component: MapView,
        props: route => ({
            features: route.meta.features,
            selectedFeatures: route.meta.selectedFeatures
        })
    },
    {
        path: '/table',
        component: TableView,
        props: route => ({
            features: route.meta.features,
            selectedFeatures: route.meta.selectedFeatures
        })
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
