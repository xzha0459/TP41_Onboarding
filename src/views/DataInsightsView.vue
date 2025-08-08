<template>
  <div class="data-insights">
    <h1>Data Insights</h1>
    <p>Vehicle ownership and population growth analysis for Melbourne</p>

    <div class="insights-grid">
      <div class="insight-card">
        <h3>📈 Vehicle Registration Growth</h3>
        <p>Historical trends and year-over-year percentages</p>
        <div class="chart-placeholder">Chart Component Coming Soon...</div>
      </div>

      <div class="insight-card">
        <h3>👥 CBD Population Growth</h3>
        <p>Population density changes from 2001-2021</p>
        <div class="chart-placeholder">Interactive Map Coming Soon...</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Data insights logic will be implemented here
</script>

<style scoped>
.data-insights {
  max-width: 1200px;
  margin: 0 auto;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.insight-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-placeholder {
  height: 200px;
  background: #f8f9fa;
  border: 2px dashed #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 15px;
  border-radius: 4px;
  color: #6c757d;
}
</style>
