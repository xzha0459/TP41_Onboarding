<template>
  <section class="container">
    <h1>Parking Forecast</h1>

    <!-- 表单 -->
    <form class="form" @submit.prevent="onSubmit">
      <input class="input" v-model="address" placeholder="Destination address…" />
      <input class="input" type="datetime-local" v-model="dtLocal" />
      <input class="input" v-model.number="maxWalk" type="number" min="1" step="1" />
      <button class="btn" :disabled="loading || !address.trim() || !dtLocal">Check</button>
    </form>

    <!-- 地图（按预测概率着色） -->
    <GoogleParkingMap :markers="markers" />

    <p v-if="loading">Checking…</p>
    <p v-else-if="error" class="error">{{ error }}</p>

    <!-- 列表 -->
    <div v-else>
      <div v-for="p in results" :key="p.kerbside_id" class="card">
        <div class="bar"><div class="fill" :style="{ width: probToPercent(p) }"></div></div>
        <div class="row">
          <strong>{{ probToPercent(p) }}</strong> available
          · zone {{ p.zone_number }} · {{ p.status_description }}
          · {{ p.distance_km.toFixed(2) }} km · walk {{ p.walk_time }} min
        </div>
      </div>
      <p v-if="!results.length && checked">No predictions.</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import axios from "axios";
import GoogleParkingMap from "@/components/maps/GoogleParkingMap.vue";
import { fetchNearbyPredict, type PredictItem } from "@/services/api";

const address = ref("");
const dtLocal = ref("");
const maxWalk = ref(5);
const loading = ref(false);
const error = ref("");
const checked = ref(false);
const results = ref<PredictItem[]>([]);

function toISO(local: string) { return new Date(local).toISOString(); }
function normalizeProb(x: number) { const v = x > 1 ? x / 100 : x; return Math.max(0, Math.min(1, v)); }
function probToPercent(p: PredictItem) { return `${Math.round(normalizeProb(p.predicted_available_probability) * 100)}%`; }

function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data
      ? (typeof err.response.data === "string" ? err.response.data : JSON.stringify(err.response.data))
      : "";
    return `Request failed (${err.response?.status ?? ""}) ${detail}`;
  }
  if (err instanceof Error) return err.message;
  return "Request failed";
}

const markers = computed(() =>
  results.value.map(p => ({
    lat: p.latitude,
    lng: p.longitude,
    probability: normalizeProb(p.predicted_available_probability),
    label: `Pred avail: ${probToPercent(p)} • zone ${p.zone_number}`,
  }))
);

async function onSubmit() {
  loading.value = true; error.value = ""; checked.value = true; results.value = [];
  try {
    const body: { address: string; datetime: string; max_walk_time?: number } = {
      address: address.value.trim(),
      datetime: toISO(dtLocal.value),
    };
    if (Number(maxWalk.value) && Number(maxWalk.value) !== 5) {
      body.max_walk_time = Number(maxWalk.value);
    }
    results.value = await fetchNearbyPredict(body);
  } catch (err: unknown) {
    error.value = getErrorMessage(err);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.container { max-width: 980px; margin: 0 auto; padding: 16px; }
.form { display: grid; grid-template-columns: 1fr 220px 120px 120px; gap: 8px; margin-bottom: 12px; }
.input { padding: 8px; border: 1px solid #ddd; border-radius: 6px; }
.btn { padding: 8px 12px; border: 0; border-radius: 8px; cursor: pointer; }

.card { padding: 10px; border: 1px solid #eee; border-radius: 10px; margin: 8px 0; }
.bar { height: 12px; background: #eee; border-radius: 8px; overflow: hidden; margin-bottom: 6px; }
.fill { height: 100%; background: #67b7dc; }

.error { color: #c00; }
.row { display: flex; gap: 6px; flex-wrap: wrap; }
</style>
