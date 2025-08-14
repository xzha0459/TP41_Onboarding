<template>
  <Section title="Data Insights">
    <div class="controls">
      <label>Start
        <input type="number" v-model.number="startYear" :min="2000" :max="2100" />
      </label>
      <label>End
        <input type="number" v-model.number="endYear" :min="2000" :max="2100" />
      </label>
      <button @click="refresh" :disabled="loading">
        {{ loading ? 'Loading…' : 'Refresh' }}
      </button>
      <span v-if="error" class="err">{{ error }}</span>
    </div>

    <div class="cards">
      <!-- Card 1: CBD Population -->
      <div class="card">
        <h3>CBD Population</h3>
        <div class="chart"><canvas ref="popCanvas"></canvas></div>
        <div v-if="popAagr != null" class="meta">
          Average Annual Growth: {{ popAagr.toFixed(2) }}%
        </div>
        <p class="note">
          Description: This chart tracks resident population in <strong>Melbourne CBD (2001–2021)</strong>. It shows a steady, long-term rise; the average annual growth over this period is about <span class="highlight">0.31%</span>.
        </p>
      </div>

      <!-- Card 2: Car Ownership -->
      <div class="card">
        <h3>Car Ownership</h3>
        <div class="chart"><canvas ref="carCanvas"></canvas></div>
        <div class="meta" v-if="carAagr != null">
          Average Annual Growth: {{ carAagr.toFixed(2) }}%
        </div>
        <p class="note">
          Description: This chart shows the total number of registered vehicles for the available years 2016, 2020 and 2021. The trend is upward, with an average annual growth of about <span class="highlight">1.95%</span> (note the limited time points).
        </p>
      </div>
    </div>
  </Section>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { insightsApi } from '@/services/insight';
import type { SeriesPoint } from '@/services/insight';
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

// 你们后端的参数（按需调整）
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
  return (Math.pow(last / first, 1 / n) - 1) * 100;
}

function destroyCharts() {
  popChart?.destroy(); popChart = null;
  carChart?.destroy(); carChart = null;
}

function makeLineChart(
  el: HTMLCanvasElement,
  labels: (string|number)[],
  data: number[],
  title: string
) {
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

    // 2) Car ownership —— 兼容两种结构：years+vehicleCounts 或 values/vehiclesPer1000
    const car: any = await insightsApi.carOwnership(STATE_CODE, startYear.value, endYear.value);

    let series: SeriesPoint[] = [];
    let yearsList: number[] | undefined;

    if (Array.isArray(car.years) && Array.isArray(car.vehicleCounts)) {
      // 在分支里用局部 const，避免出现 number[] | undefined
      const yearsList = car.years.map((y: any) => Number(y));
      series = yearsList.map((y: number, i: number) => ({
        year: y,
        value: Number(car.vehicleCounts[i])
      }));
    } else {
      const raw = car.vehiclesPer1000 ?? car.values ?? car.data ?? [];
      series = raw
        .map((p: any) => ({ year: Number(p.year ?? p.Year ?? p.y), value: Number(p.value) }))
        .filter((p: SeriesPoint) => Number.isFinite(p.year) && Number.isFinite(p.value));
    }


    if (!series.length) {
      console.warn('Unexpected carOwnership shape:', car);
      error.value = 'No car ownership data returned';
    } else {
      const carLabels = series.map(p => p.year);
      const carData   = series.map(p => p.value);
      carAagr.value   = computeAagr(series);

      if (carCanvas.value) {
        // 注意：当前数据是“Vehicles”总量，不是 per 1000
        carChart = makeLineChart(carCanvas.value, carLabels, carData, 'Vehicles');
      }
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
.controls{
  display:flex; gap:.75rem; align-items:end; margin-bottom:.75rem
}
.controls label{display:flex; flex-direction:column; gap:.25rem}
.controls input{border:1px solid #e5e7eb; border-radius:8px; padding:.4rem .6rem; width:8rem}
.controls button{padding:.46rem .9rem; border-radius:8px; background:black; color:#fff}
.err{color:#b91c1c; font-size:.9rem}

/* 上下布局（永远一列） */
.cards{
  display:grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.card{border:1px solid #e5e7eb; border-radius:16px; padding:12px}
.chart{height:300px} /* 给 canvas 一个实际高度 */
.meta{font-size:.85rem; opacity:.8; margin-top:.5rem}
.note{font-size:.85rem; margin-top:.25rem; opacity:.9}
.highlight{font-weight:700; color:#0d6efd; background:#e7f1ff; padding:0 .25rem; border-radius:4px}
</style>
