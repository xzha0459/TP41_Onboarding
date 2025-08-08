<template>
  <header style="padding:12px; border-bottom:1px solid #eee; display:flex; gap:12px;">
    <router-link to="/insights">Data Insights</router-link>
    <router-link to="/parking">Parking Map</router-link>
    <router-link to="/forecast">Forecast</router-link>
    <router-link to="/history">History</router-link>
    <router-link to="/green">Green Options</router-link>
  </header>
  <main style="padding:16px;">
    <router-view />
  </main>
</template>
