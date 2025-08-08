import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', redirect: '/insights' },
  { path: '/insights', name: 'Insights', component: () => import('../views/InsightsView.vue') },
  { path: '/parking', name: 'ParkingMap', component: () => import('../views/ParkingMapView.vue') },
  { path: '/forecast', name: 'ParkingForecast', component: () => import('../views/ParkingForecastView.vue') },
  { path: '/history', name: 'ParkingHistory', component: () => import('../views/ParkingHistoryView.vue') },
  { path: '/green', name: 'GreenOptions', component: () => import('../views/GreenOptionsView.vue') },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
