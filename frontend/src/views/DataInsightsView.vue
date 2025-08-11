<template>
  <div class="p-6 space-y-6 data-insights">
    <header class="space-y-2">
      <h1 class="text-2xl font-semibold">Data Insights</h1>
      <p class="text-sm opacity-80">CBD population & VIC registrations</p>
    </header>

    <!-- Controls -->
    <div class="flex flex-wrap items-end gap-4">
      <label class="flex flex-col">
        <span class="text-xs uppercase tracking-wide">Start Year</span>
        <select v-model.number="startYear" class="border rounded px-3 py-2 w-40">
          <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
        </select>
      </label>
      <label class="flex flex-col">
        <span class="text-xs uppercase tracking-wide">End Year</span>
        <select v-model.number="endYear" class="border rounded px-3 py-2 w-40">
          <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
        </select>
      </label>
      <button @click="refresh" class="px-4 py-2 rounded bg-black text-white hover:opacity-90">Refresh</button>
      <span v-if="loading" class="text-sm">Loading…</span>
      <span v-if="error" class="text-sm text-red-600">{{ error }}</span>
    </div>

    <!-- Sections -->
    <Section title="Population–Traffic Analysis">
      <div class="chart h-72">
        <canvas id="popChart"></canvas>
      </div>
      <div v-if="popAagr != null" class="text-xs opacity-70 mt-2">
        CBD Average Annual Growth: {{ popAagr.toFixed(2) }}%
      </div>
    </Section>

    <Section title="Car Ownership Trend (VIC)">
      <div class="chart h-72">
        <canvas id="vehChart"></canvas>
      </div>
      <div v-if="vehAagr != null" class="text-xs opacity-70 mt-2">
        Registrations Average Annual Growth: {{ vehAagr.toFixed(2) }}%
      </div>
    </Section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import Section from '../components/BaseSection.vue'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

type Point = { year: number; value: number }

// Year options (cover both datasets)
const yearOptions = Array.from({ length: 2021 - 2001 + 1 }, (_, i) => 2001 + i)
const startYear = ref(2016) // VIC data starts 2016
const endYear = ref(2021)

const loading = ref(false)
const error = ref<string | null>(null)

const popSeries = ref<Point[]>([])
const vehSeries = ref<Point[]>([])
const popAagr = ref<number | null>(null)
const vehAagr = ref<number | null>(null)

let popChart: Chart | null = null
let vehChart: Chart | null = null

function clampYears() {
  // Keep years inside options and ordered
  startYear.value = Math.min(Math.max(startYear.value, yearOptions[0]), yearOptions.at(-1)!)
  endYear.value = Math.min(Math.max(endYear.value, yearOptions[0]), yearOptions.at(-1)!)
  if (startYear.value > endYear.value) {
    const t = startYear.value
    startYear.value = endYear.value
    endYear.value = t
  }
}

async function apiGet(path: string) {
  const url = path.startsWith('/') ? path : `/${path}`
  const r = await fetch(url)
  const j = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`)
  return j
}

function normalizeValues(j: any): Point[] {
  if (Array.isArray(j.values)) return j.values.map((x: any) => ({ year: x.year, value: x.value }))
  if (Array.isArray(j.items))  return j.items.map((x: any)  => ({ year: x.year, value: x.value ?? x.total ?? x.population }))
  return []
}

function destroyCharts() {
  if (popChart) { popChart.destroy(); popChart = null }
  if (vehChart) { vehChart.destroy(); vehChart = null }
}

function drawCharts() {
  destroyCharts()

  const pCtx = (document.getElementById('popChart') as HTMLCanvasElement).getContext('2d')!
  popChart = new Chart(pCtx, {
    type: 'line',
    data: {
      labels: popSeries.value.map(p => p.year),
      datasets: [{ label: 'CBD Population', data: popSeries.value.map(p => p.value), tension: 0.2, pointRadius: 2 }],
    },
    options: { responsive: true, maintainAspectRatio: false }
  })

  const vCtx = (document.getElementById('vehChart') as HTMLCanvasElement).getContext('2d')!
  vehChart = new Chart(vCtx, {
    type: 'bar',
    data: {
      labels: vehSeries.value.map(p => p.year),
      datasets: [{ label: 'VIC Registrations', data: vehSeries.value.map(p => p.value) }],
    },
    options: { responsive: true, maintainAspectRatio: false }
  })
}

async function fetchData() {
  clampYears()
  loading.value = true
  error.value = null

  const popUrl = `/insights/cbdPopulation?startYear=${Math.max(2001, startYear.value)}&endYear=${endYear.value}`
  const vehUrl = `/insights/carOwnership?startYear=${Math.max(2016, startYear.value)}&endYear=${endYear.value}`

  const [popRes, vehRes] = await Promise.allSettled([apiGet(popUrl), apiGet(vehUrl)])

  if (popRes.status === 'fulfilled') {
    popSeries.value = normalizeValues(popRes.value)
    popAagr.value = typeof popRes.value.averageAnnualGrowthRate === 'number' ? popRes.value.averageAnnualGrowthRate : null
  } else {
    popSeries.value = []
    popAagr.value = null
    error.value = error.value || popRes.reason?.message
  }

  if (vehRes.status === 'fulfilled') {
    vehSeries.value = normalizeValues(vehRes.value)
    vehAagr.value = typeof vehRes.value.averageAnnualGrowthRate === 'number' ? vehRes.value.averageAnnualGrowthRate : null
  } else {
    vehSeries.value = []
    vehAagr.value = null
    // don't overwrite a more specific error if we already have one
    error.value = error.value || vehRes.reason?.message
  }

  drawCharts()
  loading.value = false
}

function refresh() { fetchData() }

onMounted(fetchData)
watch([startYear, endYear], fetchData)
</script>

<style scoped>
.data-insights { font-family: system-ui, -apple-system, Segoe UI, Roboto, Inter, Arial, sans-serif; }
.chart { height: 18rem; }
</style>