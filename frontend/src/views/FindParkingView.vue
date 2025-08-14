<template>
  <section class="container">
    <div class="page-header">
      <div class="left-section">
        <h1>Find Parking</h1>
        <div class="search-controls">
          <SearchBar @search="onSearch" />
          <div class="controls">
            <label>Max walk:
              <input v-model.number="maxWalk" type="number" min="1" max="30" class="walk-input"> min
            </label>
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

    <p v-if="loading">Loading…</p>
    <p v-else-if="error" class="error">{{ error }}</p>

    <div v-if="!loading && !error && sortedResults.length" class="main-content">
      <div class="cards">
        <article
          v-for="p in sortedResults"
          :key="p.kerbside_id"
          class="card"
          :class="{ 'selected': selectedParking?.kerbside_id === p.kerbside_id }"
          @click="showDetails(p)"
        >
          <header class="card-head">
            <span :class="['badge', p.is_occupied ? 'occupied' : 'free']">
              {{ p.is_occupied ? 'Occupied' : 'Unoccupied' }}
            </span>
            <span class="zone">Zone {{ p.zone_number }}</span>
          </header>
          <p class="meta">
            {{ p.distance_km?.toFixed(2) || '0.00' }} km • walk {{ Math.ceil((p.walk_time || 0) * 10) / 10 }} min
          </p>
          <p class="desc">{{ p.status_description }}</p>
          <div class="click-hint">Click for details</div>
        </article>
      </div>

      <teleport to="body">
        <div v-if="selectedParking" class="modal-overlay" @click="closeDetails">
          <div class="modal" @click.stop>
            <header class="modal-header">
              <h3>Parking Details</h3>
              <button class="close-btn" @click="closeDetails">&times;</button>
            </header>
            <div class="modal-content">
              <div class="detail-row">
                <span class="label">Status:</span>
                <span :class="['badge', selectedParking.is_occupied ? 'occupied' : 'free']">
                  {{ selectedParking.is_occupied ? 'Occupied' : 'Unoccupied' }}
                </span>
              </div>
              <div class="detail-row">
                <span class="label">Zone:</span>
                <span>{{ selectedParking.zone_number }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Distance:</span>
                <span>{{ selectedParking.distance_km?.toFixed(2) || '0.00' }} km</span>
              </div>
              <div class="detail-row">
                <span class="label">Walk Time:</span>
                <span>{{ Math.ceil((selectedParking.walk_time || 0) * 10) / 10 }} minutes</span>
              </div>
              <div class="detail-row">
                <span class="label">Last Updated:</span>
                <span>{{ selectedParking.last_updated || 'Not available' }}</span>
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
              <button class="btn btn-primary" @click="openInMaps(selectedParking)">
                Open in Maps
              </button>
              <button class="btn btn-secondary" @click="closeDetails">
                Close
              </button>
            </div>
          </div>
        </div>
      </teleport>
    </div>

    <!-- 无结果提示 -->
    <p v-if="!loading && !error && searched && !sortedResults.length" class="no-results">
      No parking available in this area...
    </p>

  </section>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import GoogleParkingMap from "@/components/maps/GoogleParkingMap.vue";
import SearchBar from "@/components/SearchBar.vue";
import ParkingLegend from "@/components/ParkingLegend.vue"; // 导入ParkingLegend组件
import { fetchNearbyWithOrigin, type NearbyItem, type OriginDTO } from "@/services/api";

const maxWalk = ref(5);
const loading = ref(false);
const error = ref("");
const searched = ref(false);
const results = ref<NearbyItem[]>([]);
const selectedParking = ref<NearbyItem | null>(null);
const origin = ref<OriginDTO | null>(null);

async function onSearch(address: string) {
  loading.value = true;
  error.value = "";
  searched.value = true;

  try {
    const body: any = { address };
    if (maxWalk.value !== 5) body.max_walk_time = maxWalk.value;
    const response = await fetchNearbyWithOrigin(body);
    results.value = response.nearby;
    origin.value = response.origin;
  } catch (err: any) {
    error.value = err?.response?.data || err?.message || "Request failed";
  } finally {
    loading.value = false;
  }
}

const sortedResults = computed(() =>
  [...results.value].sort((a, b) => (a.distance_km || 0) - (b.distance_km || 0))
);

const markers = computed(() =>
  sortedResults.value.map(p => ({
    lat: p.latitude,
    lng: p.longitude,
    occupied: p.is_occupied,
    label: `${p.zone_number} • ${p.status_description} • ${p.distance_km?.toFixed(2) || '0.00'} km • ${Math.ceil((p.walk_time || 0) * 10) / 10} min`,
  }))
);

function showDetails(parking: NearbyItem) {
  selectedParking.value = parking;
  try {
    document.body.style.overflow = 'hidden';
  } catch {}
}

function closeDetails() {
  selectedParking.value = null;
  try {
    document.body.style.overflow = '';
  } catch {}
}

function openInMaps(parking: NearbyItem) {
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

/* 页面头部布局 */
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

/* 控制区域样式调整 */
.controls {
  display: flex;
  align-items: center;
}

.controls label {
  color: #6c757d;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
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

.controls {
  display: flex;
  align-items: center;
}

.controls label {
  color: #6c757d;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.walk-input {
  width: 50px;
  margin: 0 4px;
  padding: 4px;
  background: #ffffff;
  border: 1px solid #e1e5e9;
  color: #1a1a1a;
  border-radius: 4px;
}

.error {
  color: #dc3545;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 8px;
  border-radius: 6px;
  margin: 12px 0;
}

.no-results {
  color: #1a1a1a;
  text-align: center;
  margin: 20px 0;
  font-style: italic;
  font-size: 20px;
  font-weight: 700;
}

.main-content {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.cards {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.card {
  background: #ffffff;
  border: 1px solid #e1e5e9;
  border-radius: 12px;
  padding: 12px 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,.1);
  cursor: pointer;
  transition: all 0.2s ease;
}

.card:hover {
  border-color: #0d6efd;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,.15);
}

.card.selected {
  border-color: #0d6efd;
  background: #f8f9fa;
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.2);
}

/* Modal styles */
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

.modal-actions {
  padding: 16px 20px;
  border-top: 1px solid #e1e5e9;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  background: #f8f9fa;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.badge {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 18px;
  border: 1px solid transparent;
  color: white;
}

.badge.free {
  background: #198754;
  border-color: #198754;
}

.badge.occupied {
  background: #dc3545;
  border-color: #dc3545;
}

.zone {
  color: #6c757d;
  font-size: 12px;
}

.meta {
  color: #1a1a1a;
  font-size: 13px;
  margin: 2px 0;
}

.desc {
  color: #6c757d;
  font-size: 13px;
  margin-bottom: 4px;
}

.click-hint {
  font-size: 11px;
  color: #6c757d;
  text-align: center;
  margin-top: 8px;
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

 .detail-row {
   display: flex;
   justify-content: space-between;
   align-items: center;
   padding: 8px 0;
   border-bottom: 1px solid #f8f9fa;
 }

 .detail-row:last-child {
   border-bottom: none;
 }

 .label {
   font-weight: 600;
   color: #6c757d;
   min-width: 100px;
 }

 .btn-primary {
   background: #0d6efd;
   color: white;
   padding: 8px 16px;
   border: none;
   border-radius: 6px;
   cursor: pointer;
 }

 .btn-primary:hover {
   background: #0b5ed7;
 }

 .btn-secondary {
   background: #6c757d;
   color: white;
   padding: 8px 16px;
   border: none;
   border-radius: 6px;
   cursor: pointer;
 }

 .btn-secondary:hover {
   background: #5c636a;
 }
 </style>
