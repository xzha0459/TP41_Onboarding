<template>
  <div class="parking-map-container">
    <h2>Melbourne CBD Real-time Parking Finder</h2>
    <div class="map-wrapper">
      <!-- Map component placeholder -->
      <div class="map-placeholder">
        <p>🗺️ Map Component Under Development...</p>
        <p>Melbourne CBD Center: -37.8136, 144.9631</p>
        <div class="mock-controls">
          <button @click="toggleRealTime" :class="{ active: realTimeEnabled }">
            {{ realTimeEnabled ? '✅' : '❌' }} Real-time Updates
          </button>
          <button @click="showAvailableOnly">🟢 Show Available Only</button>
          <button @click="showGreenOptions">🌱 Green Parking Options</button>
        </div>

        <!-- Mock parking spots list -->
        <div class="mock-spots">
          <h3>Sample Parking Spots:</h3>
          <div class="spot-list">
            <div class="spot-item available">
              <span class="status-indicator">🟢</span>
              <span class="address">Collins Street - Spot #A1</span>
              <span class="price">$4.50/hour</span>
            </div>
            <div class="spot-item occupied">
              <span class="status-indicator">🔴</span>
              <span class="address">Bourke Street - Spot #B2</span>
              <span class="price">$3.80/hour</span>
            </div>
            <div class="spot-item available">
              <span class="status-indicator">🟢</span>
              <span class="address">Flinders Street - Spot #C3</span>
              <span class="price">$5.20/hour</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const realTimeEnabled = ref(false)

const toggleRealTime = () => {
  realTimeEnabled.value = !realTimeEnabled.value
  console.log('Real-time updates:', realTimeEnabled.value)
}

const showAvailableOnly = () => {
  console.log('Show available parking spots only')
}

const showGreenOptions = () => {
  console.log('Show green parking options')
}
</script>

<style scoped>
.parking-map-container {
  padding: 20px;
}

.map-wrapper {
  margin-top: 20px;
}

.map-placeholder {
  min-height: 500px;
  border: 2px dashed #ccc;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
}

.mock-controls {
  margin: 20px 0;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background: #007bff;
  color: white;
  cursor: pointer;
  font-size: 14px;
}

button.active {
  background: #28a745;
}

button:hover {
  opacity: 0.8;
}

.mock-spots {
  margin-top: 30px;
  text-align: left;
  width: 100%;
  max-width: 400px;
}

.spot-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
}

.spot-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  border-radius: 6px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.spot-item.available {
  border-left: 4px solid #28a745;
}

.spot-item.occupied {
  border-left: 4px solid #dc3545;
}

.status-indicator {
  font-size: 16px;
  margin-right: 10px;
}

.address {
  flex: 1;
  font-weight: 500;
}

.price {
  color: #6c757d;
  font-size: 14px;
}
</style>
