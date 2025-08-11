<template>
  <section class="container">
    <h1>Parking Forecast</h1>

    <ForecastSearchBar :loading="loading" @search="handleSearch" />


    <GoogleParkingMap :markers="markers" />

    <p v-if="loading">Loading...</p>
    <p v-else-if="error" class="error">{{ error }}</p>


    <div v-if="!loading && !error && results.length" class="cards">
      <div v-for="p in results" :key="p.kerbside_id" class="card">
        <div class="prob">{{ getPercent(p) }} available</div>
        <div class="info">Zone {{ p.zone_number }} • {{ p.distance_km.toFixed(1) }}km • {{ p.walk_time }}min</div>
      </div>
    </div>


    <p v-if="!loading && !error && searched && !results.length" class="no-results">
      No parking available in this area...
    </p>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import GoogleParkingMap from "@/components/maps/GoogleParkingMap.vue";
import ForecastSearchBar from "../components/ForecastSearchBar.vue";
import { fetchNearbyPredict, type PredictItem } from "@/services/api";

const loading = ref(false);
const error = ref("");
const results = ref<PredictItem[]>([]);
const searched = ref(false);

async function handleSearch(data: { address: string; date: string; time: string; maxWalk: number }) {
  loading.value = true;
  error.value = "";
  searched.value = true; // 关键：设置搜索状态为 true

  try {
    const datetime = new Date(`${data.date}T${data.time}`).toISOString();
    const body: any = { address: data.address, datetime };
    if (data.maxWalk !== 5) body.max_walk_time = data.maxWalk;

    results.value = await fetchNearbyPredict(body);
  } catch (err: any) {
    error.value = err?.response?.data || err?.message || "Failed";
  } finally {
    loading.value = false;
  }
}

function getPercent(p: PredictItem) {
  const prob = p.predicted_available_probability > 1
    ? p.predicted_available_probability / 100
    : p.predicted_available_probability;
  return Math.round(prob * 100) + '%';
}

const markers = computed(() =>
  results.value.map(p => ({
    lat: p.latitude,
    lng: p.longitude,
    probability: p.predicted_available_probability > 1
      ? p.predicted_available_probability / 100
      : p.predicted_available_probability,
    label: `${getPercent(p)} available • Zone ${p.zone_number}`,
  }))
);
</script>

<style scoped>
.container {
  max-width: 980px;
  margin: 0 auto;
  padding: 16px;
}

.error {
  color: #dc3545;
  margin: 12px 0;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 8px;
  border-radius: 6px;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.card {
  background: #f8f9fa;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 12px;
}

.prob {
  font-size: 16px;
  font-weight: bold;
  color: #198754;
  margin-bottom: 4px;
}

.info {
  color: #6c757d;
  font-size: 14px;
}

.no-results {
  color: #1a1a1a;
  text-align: center;
  margin: 20px 0;
  font-style: italic;
}
</style>
