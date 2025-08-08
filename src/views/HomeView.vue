<template>
  <div class="home">
    <h1>Melbourne Parking Assistant</h1>
    <p>Help Melbourne commuters find parking spots quickly and reduce search time</p>

    <div class="features">
      <div class="feature-card">
        <h3>🗺️ Real-time Parking</h3>
        <p>View real-time parking availability in CBD areas</p>
        <RouterLink to="/parking" class="btn">Find Parking</RouterLink>
      </div>

      <div class="feature-card">
        <h3>📊 Data Insights</h3>
        <p>Understand vehicle ownership and population growth trends</p>
        <RouterLink to="/insights" class="btn">View Data</RouterLink>
      </div>

      <div class="feature-card">
        <h3>🌱 Eco Commute</h3>
        <p>Track your carbon footprint and choose green transportation</p>
        <RouterLink to="/eco" class="btn">Eco Mode</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.home {
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 40px;
}

.feature-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.feature-card h3 {
  margin-bottom: 10px;
  color: #495057;
}

.btn {
  display: inline-block;
  background: #007bff;
  color: white;
  padding: 8px 16px;
  text-decoration: none;
  border-radius: 4px;
  margin-top: 10px;
  transition: background 0.3s;
}

.btn:hover {
  background: #0056b3;
}
</style>
