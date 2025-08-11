<template>
  <Section title="Data Insights">
    <div class="controls">
      <label>Start
        <input type="number" v-model.number="startYear" :min="2000" :max="2100" />
      </label>
      <label>End
        <input type="number" v-model.number="endYear" :min="2000" :max="2100" />
      </label>
      <button @click="refresh" :disabled="loading">{{ loading ? 'Loading…' : 'Refresh' }}</button>
      <span v-if="error" class="err">{{ error }}</span>
    </div>

    <div class="cards">
      <div class="card">
        <h3>CBD Population</h3>
        <div class="chart"><canvas ref="popCanvas"></canvas></div>
        <div v-if="popAagr != null" class="meta">
          Average Annual Growth: {{ popAagr.toFixed(2) }}%
        </div>
      </div>

      <div class="card">
        <h3>Car Ownership (per 1000)</h3>
        <div class="chart"><canvas ref="carCanvas"></canvas></div>
        <div v-if="carAagr != null" class="meta">
          Average Annual Growth: {{ carAagr.toFixed(2) }}%
        </div>
      </div>
    </div>
  </Section>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { insightsApi, type SeriesPoint } from '@/services/insight';
import Chart from 'chart.js/auto';

const startYear = ref<number>(2001);
const endYear   = ref<number>(2021);
const loading   = ref(false);
const error     = ref<string | null>(null);

const popCanvas = ref<HTMLCanvasElement | null>(null);
const carCanvas = ref<HTMLCanvasElement | null>(null);

let popChart: Chart | null = null;
let carChart: Chart | null = null;

const popAagr = ref<number | null>(null);
const carAagr = ref<number | null>(null);

// If you don't want to run local backend, just point VITE_API_BASE_URL to your remote:
// .env.local -> VITE_API_BASE_URL=https://api-tp41.xyz
const CBD_REGION = 'CBD_MEL';
const STATE_CODE = 'VIC';

function computeAagr(points: SeriesPoint[]) {
  if (!points?.length) return null;
  const firstY = points[0]?.year;
  const lastY  = points[points.length - 1]?.year;
  const n = Math.max(1, Number(lastY) - Number(firstY));
  const first = points[0]?.value ?? 0;
  const last  = points[points.length - 1]?.value ?? 0;
  if (first <= 0 || last <= 0) return null;
  // CAGR as percentage
  return (Math.pow(last / first, 1 / n) - 1) * 100;
}

function destroyCharts() {
  popChart?.destroy(); popChart = null;
  carChart?.destroy(); carChart = null;
}

function makeLineChart(el: HTMLCanvasElement, labels: (string|number)[], data: number[], title: string) {
  return new Chart(el.getContext('2d')!, {
    type: 'line',
    data: {
      labels,
      datasets: [{ label: title, data, tension: 0.2, pointRadius: 2 }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { x: { grid: { display: false } }, y: { beginAtZero: false } },
      plugins: { legend: { display: true } }
    }
  });
}

async function refresh() {
  loading.value = true;
  error.value = null;
  destroyCharts();

  try {
    // 1) Population
    const pop = await insightsApi.cbdPopulation(CBD_REGION, startYear.value, endYear.value);
    const popLabels = pop.values.map(p => p.year);
    const popData   = pop.values.map(p => p.value);
    popAagr.value   = computeAagr(pop.values);

    if (popCanvas.value) {
      popChart = makeLineChart(popCanvas.value, popLabels, popData, 'Population');
    }

    // 2) Car ownership per 1000
    const car = await insightsApi.carOwnership(STATE_CODE, startYear.value, endYear.value);
    // prefer vehiclesPer1000 if backend provides it; fallback to values
    const series = (car.vehiclesPer1000 && car.vehiclesPer1000.length ? car.vehiclesPer1000 : car.values) || [];
    const carLabels = series.map(p => p.year);
    const carData   = series.map(p => p.value);
    carAagr.value   = computeAagr(series);

    if (carCanvas.value) {
      carChart = makeLineChart(carCanvas.value, carLabels, carData, 'Vehicles per 1000');
    }

  } catch (e: any) {
    error.value = e?.message || 'Failed to load insights';
  } finally {
    loading.value = false;
  }
}

onMounted(() => { refresh(); });
onBeforeUnmount(destroyCharts);
</script>

<style scoped>
.controls{display:flex; gap:.75rem; align-items:end; margin-bottom:.75rem}
.controls label{display:flex; flex-direction:column; gap:.25rem}
.controls input{border:1px solid #e5e7eb; border-radius:8px; padding:.4rem .6rem; width:8rem}
.controls button{padding:.46rem .9rem; border-radius:8px; background:black; color:#fff}
.err{color:#b91c1c; font-size:.9rem}

.cards{
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}


.card{border:1px solid #e5e7eb; border-radius:16px; padding:12px}
.chart{height:300px} /* give canvas a real height */
.meta{font-size:.85rem; opacity:.8; margin-top:.5rem}
</style>
