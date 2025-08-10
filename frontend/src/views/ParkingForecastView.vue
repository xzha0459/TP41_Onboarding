<template>
  <section class="container">
    <h1>Parking Forecast</h1>

    <form class="form" @submit.prevent="onSubmit">
      <input class="input" v-model="address" placeholder="Destination address…" />
      <input class="input" type="datetime-local" v-model="dtLocal" />
      <input class="input" v-model.number="maxWalk" type="number" min="1" step="1" />
      <button class="btn" :disabled="loading || !address.trim() || !dtLocal">Check</button>
    </form>

    <p v-if="loading">Checking…</p>
    <p v-else-if="error" class="error">{{ error }}</p>

    <div v-else>
      <div v-for="p in results" :key="p.kerbside_id" class="card">
        <div class="bar"><div class="fill" :style="{ width: probToPercent(p) }"></div></div>
        <div>Predicted availability: <strong>{{ probToPercent(p) }}</strong></div>
        <div>{{ p.zone_number }} · {{ p.status_description }}</div>
      </div>
      <p v-if="!results.length && checked">No predictions.</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import axios from "axios";
import { fetchNearbyPredict, type PredictItem } from "@/services/api";

const address = ref("");
const dtLocal = ref(""); // bound to datetime-local, convert to ISO on submit
const maxWalk = ref(5);
const loading = ref(false);
const error = ref("");
const checked = ref(false);
const results = ref<PredictItem[]>([]);

function toISO(local: string) {
  // datetime-local gives local time; convert to ISO with timezone
  return new Date(local).toISOString();
}

function probToPercent(p: PredictItem) {
  const x = p.predicted_available_probability;
  const pct = x > 1 ? x : x * 100; // accept 0~1 or 0~100
  return `${Math.round(pct)}%`;
}

// 把后端返回的错误体显示出来
function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data
      ? (typeof err.response.data === "string" ? err.response.data
        : JSON.stringify(err.response.data))
      : "";
    return `Request failed (${err.response?.status ?? ""}) ${detail}`;
  }
  if (err instanceof Error) return err.message;
  return "Request failed";
}

async function onSubmit() {
  loading.value = true; error.value = ""; checked.value = true; results.value = [];
  try {
    const body: { address: string; datetime: string; max_walk_time?: number } = {
      address: address.value.trim(),
      datetime: new Date(dtLocal.value).toISOString(),
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
.container { max-width: 820px; margin: 0 auto; padding: 16px; }
.form { display: grid; grid-template-columns: 1fr 220px 120px 120px; gap: 8px; }
.input { padding: 8px; border: 1px solid #ddd; border-radius: 6px; }
.btn { padding: 8px 12px; border: 0; border-radius: 8px; cursor: pointer; }
.card { padding: 10px; border: 1px solid #eee; border-radius: 10px; margin: 8px 0; }
.bar { height: 12px; background: #eee; border-radius: 8px; overflow: hidden; margin-bottom: 6px; }
.fill { height: 100%; }
.error { color: #c00; }
</style>
