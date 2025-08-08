<template>
  <div class="eco-commute">
    <h1>Eco-Conscious Commuting</h1>
    <p>Track your environmental impact and choose sustainable transportation</p>

    <div class="eco-features">
      <div class="feature-card">
        <h3>🌱 Carbon Footprint Calculator</h3>
        <p>Calculate CO2 emissions for different transport modes</p>
        <button class="btn-primary">Calculate Impact</button>
      </div>

      <div class="feature-card">
        <h3>🚌 Green Parking Options</h3>
        <p>Find parking spots near public transport</p>
        <button class="btn-primary">Find Green Spots</button>
      </div>

      <div class="feature-card">
        <h3>🏆 Environmental Achievements</h3>
        <p>Track your emission reduction progress</p>
        <button class="btn-primary">View Progress</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Eco commute logic will be implemented here
</script>

<style scoped>
.eco-commute {
  max-width: 1200px;
  margin: 0 auto;
}

.eco-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.feature-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 15px;
}

.btn-primary:hover {
  background: #218838;
}
</style>
