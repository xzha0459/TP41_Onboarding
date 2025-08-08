<template>
  <div class="parking-view">
    <div class="page-header">
      <h1>Parking Finder</h1>
      <p>Find available parking spots in Melbourne CBD in real-time</p>
    </div>
    <ParkingMap />
  </div>
</template>

<script setup lang="ts">
import ParkingMap from '@/components/maps/ParkingMap.vue'
</script>

<style scoped>
.parking-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-header p {
  color: #6c757d;
  font-size: 16px;
}
</style>
