<template>
  <section class="container">
    <h1>Find Parking</h1>

    <SearchBar @search="onSearch" />

    <div class="controls">
      <label>Max walk:
        <input v-model.number="maxWalk" type="number" min="1" max="30" class="walk-input"> min
      </label>
    </div>

    <GoogleParkingMap :markers="markers" />

    <p v-if="loading">Loading…</p>
    <p v-else-if="error" class="error">{{ error }}</p>


    <div v-if="!loading && !error && sortedResults.length" class="cards">
      <article
        v-for="p in sortedResults"
        :key="p.kerbside_id"
        class="card"
        @click="showDetails(p)"
      >
        <header class="card-head">
          <span :class="['badge', p.is_occupied ? 'occupied' : 'free']">
            {{ p.is_occupied ? 'Occupied' : 'Unoccupied' }}
          </span>
          <span class="zone">Zone {{ p.zone_number }}</span>
        </header>
        <p class="meta">
          {{ p.distance_km.toFixed(2) }} km • walk {{ p.walk_time }} min
        </p>
        <p class="desc">{{ p.status_description }}</p>
        <div class="click-hint">Click for details</div>
      </article>
    </div>

    <!-- 无结果提示 - 与 Forecast 页面一致 -->
    <p v-if="!loading && !error && searched && !sortedResults.length" class="no-results">
      No parking available in this area...
    </p>


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
            <span>{{ selectedParking.distance_km.toFixed(2) }} km</span>
          </div>
          <div class="detail-row">
            <span class="label">Walk Time:</span>
            <span>{{ selectedParking.walk_time }} minutes</span>
          </div>
          <div class="detail-row">
            <span class="label">Last Updated:</span>
            <span>{{ selectedParking.last_updated || 'Not available' }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Description:</span>
            <span>{{ selectedParking.status_description }}</span>
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
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import GoogleParkingMap from "@/components/maps/GoogleParkingMap.vue";
import SearchBar from "@/components/SearchBar.vue";
import { fetchNearby, type NearbyItem } from "@/services/api";

const maxWalk = ref(5);
const loading = ref(false);
const error = ref("");
const searched = ref(false);
const results = ref<NearbyItem[]>([]);
const selectedParking = ref<NearbyItem | null>(null);

async function onSearch(address: string) {
  loading.value = true;
  error.value = "";
  searched.value = true;

  try {
    const body: any = { address };
    if (maxWalk.value !== 5) body.max_walk_time = maxWalk.value;
    results.value = await fetchNearby(body);
  } catch (err: any) {
    error.value = err?.response?.data || err?.message || "Request failed";
  } finally {
    loading.value = false;
  }
}

const sortedResults = computed(() =>
  [...results.value].sort((a, b) => a.distance_km - b.distance_km)
);

const markers = computed(() =>
  sortedResults.value.map(p => ({
    lat: p.latitude,
    lng: p.longitude,
    occupied: p.is_occupied,
    label: `${p.zone_number} • ${p.status_description} • ${p.distance_km.toFixed(2)} km • ${p.walk_time} min`,
  }))
);

function showDetails(parking: NearbyItem) {
  selectedParking.value = parking;
}

function closeDetails() {
  selectedParking.value = null;
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

.controls {
  margin: 12px 0;
}

.controls label {
  color: #6c757d;
  font-size: 14px;
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
}

.cards {
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
  max-width: 500px;
  width: 90%;
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
}

.modal-header h3 {
  margin: 0;
  color: #1a1a1a;
}

.close-btn {
  background: none;
  border: none;
  color: #6c757d;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #1a1a1a;
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

.detail-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: #6c757d;
  min-width: 100px;
}

.modal-actions {
  padding: 16px 20px;
  border-top: 1px solid #e1e5e9;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
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
