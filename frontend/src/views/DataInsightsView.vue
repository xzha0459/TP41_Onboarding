<template>
  <div class="p-6 space-y-6 data-insights">
    <header class="space-y-2">
      <h1 class="text-2xl font-semibold">Data Insights</h1>
      <p class="text-sm opacity-80">CBD population (live) + vehicles (placeholder)</p>
    </header>

    <!-- Controls -->
    <div class="flex flex-wrap items-end gap-4">
      <label class="flex flex-col">
        <span class="text-xs uppercase tracking-wide">Start Year</span>
        <input type="number" v-model.number="startYear" min="2001" max="2025" class="border rounded px-3 py-2 w-32" />
      </label>

      <label class="flex flex-col">
        <span class="text-xs uppercase tracking-wide">End Year</span>
        <input type="number" v-model.number="endYear" min="2001" max="2025" class="border rounded px-3 py-2 w-32" />
      </label>

      <button @click="refresh" class="px-4 py-2 rounded bg-black text-white hover:opacity-90">
        Refresh
      </button>

      <span v-if="loading" class="text-sm">Loading…</span>
      <span v-if="error" class="text-sm text-red-600">{{ error }}</span>
    </div>

    <!-- Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Vehicles (placeholder) -->
      <section class="card rounded-2xl border p-4 space-y-3 relative">
        <div class="flex items-baseline justify-between">
          <h3 class="font-medium">📈 Vehicle Registration Growth</h3>
          <span class="text-xs px-2 py-0.5 rounded-full border opacity-70">Average Annual Growth</span>
        </div>
        <div class="chart h-72 relative">
          <canvas id="vehChart"></canvas>
          <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          </div>
        </div>
      </section>

      <!-- Population (live) -->
      <section class="card rounded-2xl border p-4 space-y-3">
        <div class="flex items-baseline justify-between">
          <h3 class="font-medium">👥 CBD Population</h3>
          <div v-if="popAagr != null" class="text-xs opacity-70">
            Average Annual Growth: {{ popAagr.toFixed(2) }}%
          </div>
        </div>
        <div class="chart h-72">
          <canvas id="popChart"></canvas>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

// Years (defaults fit your data ranges)
const startYear = ref(2016)
const endYear = ref(2021)

const loading = ref(false)
const error = ref<string | null>(null)

// Population series + metric
type Point = { year: number; value: number }
const popSeries = ref<Point[]>([])
const popAagr = ref<number | null>(null)

// Charts
let vehChart: Chart | null = null
let popChart: Chart | null = null

function yearsArray(a: number, b: number): number[] {
  const start = Math.min(a, b), end = Math.max(a, b)
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
}

function destroyCharts() {
  if (vehChart) { vehChart.destroy(); vehChart = null }
  if (popChart) { popChart.destroy(); popChart = null }
}

function drawVehiclePlaceholder() {
  // simple zeroed bars to keep layout consistent (no backend call)
  const labels = yearsArray(startYear.value, endYear.value)
  const data = labels.map(() => 0)
  const ctx = (document.getElementById('vehChart') as HTMLCanvasElement).getContext('2d')!
  vehChart = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets: [{ label: 'Registrations', data }] },
    options: { responsive: true, maintainAspectRatio: false }
  })
}

async function apiGet(path: string) {
  // ensure leading slash so Vite proxy routes to Django
  const url = path.startsWith('/') ? path : `/${path}`
  const r = await fetch(url)
  const j = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`)
  return j
}

function normalizePopulationPayload(j: any): Point[] {
  if (Array.isArray(j.items)) {
    return j.items.map((x: any) => ({ year: x.year, value: (x.population ?? x.value) as number }))
  }
  if (Array.isArray(j.values)) {
    return j.values.map((x: any) => ({ year: x.year, value: x.value as number }))
  }
  return []
}

async function fetchPopulation() {
  loading.value = true
  error.value = null
  try {
    const pop = await apiGet(`/insights/cbdPopulation?startYear=${Math.max(2001, startYear.value)}&endYear=${endYear.value}`)
    popSeries.value = normalizePopulationPayload(pop)
    popAagr.value = typeof pop.averageAnnualGrowthRate === 'number' ? pop.averageAnnualGrowthRate : null

    // draw charts
    destroyCharts()
    drawVehiclePlaceholder()
    const pCtx = (document.getElementById('popChart') as HTMLCanvasElement).getContext('2d')!
    popChart = new Chart(pCtx, {
      type: 'line',
      data: {
        labels: popSeries.value.map(p => p.year),
        datasets: [{ label: 'Population', data: popSeries.value.map(p => p.value), tension: 0.2, pointRadius: 2 }],
      },
      options: { responsive: true, maintainAspectRatio: false }
    })
  } catch (e: any) {
    error.value = e?.message ?? String(e)
    destroyCharts()
    // still render placeholder so the grid doesn't shift
    drawVehiclePlaceholder()
  } finally {
    loading.value = false
  }
}

function refresh() {
  if (Number.isFinite(startYear.value) && Number.isFinite(endYear.value)) {
    fetchPopulation()
  }
}

onMounted(fetchPopulation)
watch([startYear, endYear], fetchPopulation)
</script>

<style scoped>
.data-insights { font-family: system-ui, -apple-system, Segoe UI, Roboto, Inter, Arial, sans-serif; }
.card { background: white; }
.chart { height: 18rem; }
</style>
