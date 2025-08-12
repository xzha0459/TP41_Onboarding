import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', redirect: '/find' },
  { path: '/insights', name: 'Insights', component: () => import('../views/DataInsightsView.vue') },
  { path: '/find', name: 'FindParking', component: () => import('../views/FindParkingView.vue') },
  { path: '/forecast', name: 'ParkingForecast', component: () => import('../views/ParkingForecastView.vue') },
  { path: '/trends', name: 'ParkingTrends', component: () => import('../views/ParkingTrendsView.vue') },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
