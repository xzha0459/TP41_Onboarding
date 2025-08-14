<template>
  <section class="container">
    <div class="page-header">
      <div class="left-section">
        <h1>Parking Forecast</h1>
        <div class="search-controls">
          <ForecastSearchBar :loading="loading" @search="handleSearch" />
          <div class="prob-legend">
            <span class="dot green"></span><span>Highly recommended</span>
            <span class="sep">|</span>
            <span class="dot yellow"></span><span>Recommended</span>
            <span class="sep">|</span>
            <span class="dot red"></span><span>Not recommended</span>
          </div>
        </div>
      </div>
      <div class="right-section">
        <ParkingLegend class="legend-card" />
      </div>
    </div>

    <GoogleParkingMap :markers="markers" :origin="origin" />

    <div v-if="loading" class="map-loading-overlay">
      <div class="loading-spinner"></div>
      <span>Searching for parking...</span>
    </div>

    <p v-if="loading">Loading...</p>
    <p v-else-if="error" class="error">{{ error }}</p>

    <div v-if="!loading && !error && results.length" class="cards">
      <div
        v-for="p in results"
        :key="p.kerbside_id"
        class="card"
        :class="{ selected: selectedParking?.kerbside_id === p.kerbside_id }"
        @click="showDetails(p)"
      >
        <div class="prob">{{ getPercent(p) }} available</div>
        <div class="info">Zone {{ p.zone_number }} • {{ (p.distance_km || 0).toFixed(1) }}km • {{ p.walk_time || 0 }}min</div>
      </div>
    </div>

    <teleport to="body">
      <div v-if="selectedParking" class="modal-overlay" @click="closeDetails">
        <div class="modal" @click.stop>
          <header class="modal-header">
            <h3>Parking Forecast Details</h3>
            <button class="close-btn" @click="closeDetails">&times;</button>
          </header>
          <div class="modal-content">
            <div class="detail-row">
              <span class="label">Predicted Availability:</span>
              <span>{{ getPercent(selectedParking) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Zone:</span>
              <span>{{ selectedParking.zone_number }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Distance:</span>
              <span>{{ (selectedParking.distance_km || 0).toFixed(2) }} km</span>
            </div>
            <div class="detail-row">
              <span class="label">Walk Time:</span>
              <span>{{ Math.ceil((selectedParking.walk_time || 0) * 10) / 10 }} minutes</span>
            </div>
            <div class="detail-row">
              <span class="label">Description:</span>
              <span>{{ selectedParking.sign_text }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Location:</span>
              <span>{{ selectedParking.latitude.toFixed(6) }}, {{ selectedParking.longitude.toFixed(6) }}</span>
            </div>
          </div>
          <div class="modal-actions">
            <button class="btn btn-primary" @click="openInMaps(selectedParking)">Open in Maps</button>
            <button class="btn btn-secondary" @click="closeDetails">Close</button>
          </div>
        </div>
      </div>
    </teleport>

    <p v-if="!loading && !error && searched && !results.length" class="no-results">
      No parking available in this area...
    </p>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import GoogleParkingMap from "@/components/maps/GoogleParkingMap.vue";
import ForecastSearchBar from "../components/ForecastSearchBar.vue";
import ParkingLegend from "@/components/ParkingLegend.vue"; // 导入ParkingLegend组件
import { fetchNearbyPredictWithOrigin, type PredictItem, type OriginDTO } from "@/services/api";

const loading = ref(false);
const error = ref("");
const results = ref<PredictItem[]>([]);
const searched = ref(false);
const origin = ref<OriginDTO | null>(null);
const selectedParking = ref<PredictItem | null>(null);

async function handleSearch(data: { address: string; date: string; time: string; maxWalk: number }) {
  loading.value = true;
  error.value = "";
  searched.value = true; // 关键：设置搜索状态为 true

  try {
    const datetime = new Date(`${data.date}T${data.time}`).toISOString();
    const body: any = { address: data.address, datetime };
    if (data.maxWalk !== 5) body.max_walk_time = data.maxWalk;

    const response = await fetchNearbyPredictWithOrigin(body);
    results.value = response.nearby;
    origin.value = response.origin;
  } catch (err: any) {
    error.value = err?.response?.data || err?.message || "Failed";
  } finally {
    loading.value = false;
  }
}

function getPercent(p: PredictItem) {
  const probability = p.predicted_available_probability ?? 0;
  const prob = probability > 1 ? probability / 100 : probability;
  return Math.round(prob * 100) + '%';
}

const markers = computed(() =>
  results.value.map(p => {
    const probability = p.predicted_available_probability ?? 0;
    const normalizedProb = probability > 1 ? probability / 100 : probability;

    return {
      lat: p.latitude,
      lng: p.longitude,
      probability: normalizedProb,
      label: `${getPercent(p)} available • Zone ${p.zone_number}`,
    };
  })
);

function showDetails(parking: PredictItem) {
  selectedParking.value = parking;
  try { document.body.style.overflow = 'hidden'; } catch {}
}

function closeDetails() {
  selectedParking.value = null;
  try { document.body.style.overflow = ''; } catch {}
}

function openInMaps(parking: PredictItem) {
  const url = `https://www.google.com/maps?q=${parking.latitude},${parking.longitude}`;
  window.open(url, '_blank');
}
</script>

<style scoped>
.container {
  max-width: 980px;
  margin: 0 auto;
  padding: 16px;
}

/* 页面头部布局 - 与FindParking保持一致 */
.page-header {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.left-section {
  flex: 1;
  min-width: 0;
}

.left-section h1 {
  margin: 0 0 16px 0;
  font-size: 24px;
  color: #1a1a1a;
}

.search-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.right-section {
  flex: 0 0 320px;
}

.legend-card {
  background: #ffffff;
  border: 1px solid #e1e5e9;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
}

/* 概率颜色说明 */
.prob-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  color: #6c757d;
  font-size: 13px;
  margin-top: 4px;
}

.prob-legend .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
  border: 1px solid rgba(0,0,0,.1);
}

.prob-legend .dot.green { background: #198754; }
.prob-legend .dot.yellow { background: #ffc107; }
.prob-legend .dot.red { background: #dc3545; }

.prob-legend .sep {
  color: #adb5bd;
  margin: 0 4px;
}

/* 在小屏幕上调整布局 */
@media (max-width: 968px) {
  .page-header {
    flex-direction: column;
    gap: 20px;
  }

  .right-section {
    flex: none;
    width: 100%;
  }

  .legend-card {
    padding: 14px;
  }
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

.card.selected {
  border-color: #0d6efd;
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.2);
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
  font-size: 20px;
  font-weight: 700;
}

/* Map loading overlay */
.map-loading-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  z-index: 100;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.map-loading-overlay span {
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
}

/* Modal styles (aligned with FindParking) */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #ffffff;
  border-radius: 12px;
  max-width: 520px;
  width: 92%;
  max-height: 80vh;
  overflow-y: auto;
  border: 1px solid #e1e5e9;
  box-shadow: 0 10px 25px rgba(0,0,0,.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e1e5e9;
  background: #f8f9fa;
}

.modal-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 16px;
}

.modal-content {
  padding: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f8f9fa;
}

.detail-row:last-child { border-bottom: none; }
.label { font-weight: 600; color: #6c757d; min-width: 140px; }

.modal-actions {
  padding: 16px 20px;
  border-top: 1px solid #e1e5e9;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  background: #f8f9fa;
}

.btn-primary {
  background: #0d6efd;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.btn-primary:hover { background: #0b5ed7; }

.btn-secondary {
  background: #6c757d;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.btn-secondary:hover { background: #5c636a; }
</style>
