import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/parking',
      name: 'parking',
      component: () => import('../views/ParkingView.vue'),
    },
    {
      path: '/insights',
      name: 'insights',
      component: () => import('../views/DataInsightsView.vue'),
    },
    {
      path: '/eco',
      name: 'eco',
      component: () => import('../views/EcoCommuteView.vue'),
    },
  ],
})

export default router
