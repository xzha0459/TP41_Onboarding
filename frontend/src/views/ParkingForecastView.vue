<template>
  <section class="container">
    <h1>Parking Forecast</h1>

    <!-- 搜索 -->
    <SearchBar @search="onSearch" />

    <!-- 控制 -->
    <div class="controls">
      <input type="date" v-model="date" class="input">
      <input type="time" v-model="time" class="input">
      <input v-model.number="maxWalk" type="number" min="1" max="30" class="walk-input" placeholder="5">
      <button @click="checkForecast" :disabled="loading || !address" class="btn">Check</button>
    </div>

    <!-- 地图 -->
    <GoogleParkingMap :markers="markers" />

    <p v-if="loading">Loading...</p>
    <p v-else-if="error" class="error">{{ error }}</p>

    <!-- 结果 -->
    <div class="cards">
      <div v-for="p in results" :key="p.kerbside_id" class="card">
        <div class="prob">{{ getPercent(p) }} available</div>
        <div class="info">Zone {{ p.zone_number }} • {{ p.distance_km.toFixed(1) }}km • {{ p.walk_time }}min</div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import GoogleParkingMap from "@/components/maps/GoogleParkingMap.vue";
import SearchBar from "@/components/SearchBar.vue";
import { fetchNearbyPredict, type PredictItem } from "@/services/api";

const address = ref("");
const date = ref("");
const time = ref("");
const maxWalk = ref(5);
const loading = ref(false);
const error = ref("");
const results = ref<PredictItem[]>([]);

// 设置默认日期时间
const now = new Date();
date.value = now.toISOString().split('T')[0];
time.value = now.toTimeString().slice(0, 5);

function onSearch(addr: string) {
  address.value = addr;
}

async function checkForecast() {
  if (!address.value) return;

  loading.value = true;
  error.value = "";

  try {
    const datetime = new Date(`${date.value}T${time.value}`).toISOString();
    const body: any = { address: address.value, datetime };
    if (maxWalk.value !== 5) body.max_walk_time = maxWalk.value;

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
.container { max-width: 980px; margin: 0 auto; padding: 16px; }

.controls {
  display: flex;
  gap: 8px;
  margin: 16px 0;
  flex-wrap: wrap;
}

.input {
  padding: 8px;
  border: 1px solid #444;
  border-radius: 6px;
  background: #2a2a2a;
  color: #fff;
}

.walk-input {
  width: 60px;
  padding: 8px;
  border: 1px solid #444;
  border-radius: 6px;
  background: #2a2a2a;
  color: #fff;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background: #2ea44f;
  color: white;
  cursor: pointer;
}

.btn:disabled {
  background: #444;
  cursor: not-allowed;
}

.error {
  color: #c00;
  margin: 12px 0;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.card {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 12px;
}

.prob {
  font-size: 16px;
  font-weight: bold;
  color: #2ea44f;
  margin-bottom: 4px;
}

.info {
  color: #ccc;
  font-size: 14px;
}
</style>
