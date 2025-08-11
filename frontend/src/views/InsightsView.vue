<template>
  <Section title="Population–Traffic Analysis">
    <div class="controls">
      <label>Start
        <input type="number" v-model.number="startYear" min="2001" max="2025" />
      </label>
      <label>End
        <input type="number" v-model.number="endYear" min="2001" max="2025" />
      </label>
      <button @click="refresh" :disabled="loading">{{ loading ? 'Loading…' : 'Refresh' }}</button>
      <span v-if="error" class="err">{{ error }}</span>
    </div>

    <div class="chart"><canvas id="popChart"></canvas></div>
    <div v-if="popAagr != null" class="meta">
      Average Annual Growth: {{ popAagr.toFixed(2) }}%
    </div>
  </Section>

  <Section title="Car Ownership (Victoria)">
    <div class="chart"><canvas id="vehChart"></canvas></div>
    <div v-if="vehCagr != null" class="meta">
      CAGR: {{ vehCagr.toFixed(2) }}%
    </div>
  </Section>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import Section from '../components/BaseSection.vue'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

const startYear = ref(2001)
const endYear   = ref(2021)
const loading   = ref(false)
const error     = ref<string | null>(null)

const popAagr = ref<number | null>(null)
const vehCagr = ref<number | null>(null)

let popChart: Chart | null = null
let vehChart: Chart | null = null

function destroyCharts() {
  if (popChart) { popChart.destroy(); popChart = null }
  if (vehChart) { vehChart.destroy(); vehChart = null }
}

function years(a:number,b:number){
  const s=Math.min(a,b), e=Math.max(a,b)
  return Array.from({length:e-s+1},(_,i)=>s+i)
}

function computeCagr(vals:number[], labels:(number|string)[]) {
  if (!vals?.length) return null
  const first = vals[0]
  const last  = vals[vals.length-1]
  // years spanned (handles non-contiguous labels)
  const firstYear = Number(labels[0])
  const lastYear  = Number(labels[labels.length-1])
  const n = Math.max(1, (isFinite(firstYear) && isFinite(lastYear)) ? (lastYear - firstYear) : (vals.length-1))
  if (first <= 0 || last <= 0 || n <= 0) return null
  return (Math.pow(last/first, 1/n) - 1) * 100
}

async function apiGet(path: string){
  const url = path.startsWith('/') ? path : `/${path}`
  const r = await fetch(url)
  const j = await r.json().catch(()=> ({}))
  if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`)
  return j
}

async function draw() {
  loading.value = true
  error.value = null
  try {
    destroyCharts()

    // ----- Population -----
    const pop = await apiGet(`/insights/cbdPopulation?startYear=${startYear.value}&endYear=${endYear.value}`)
    const popItems = Array.isArray(pop.items) ? pop.items
                    : Array.isArray(pop.values) ? pop.values
                    : []
    const popLabels = popItems.map((x:any)=> x.year ?? x.ref_year)
    const popData   = popItems.map((x:any)=> Number(x.population ?? x.value ?? 0))
    popAagr.value   = typeof pop.averageAnnualGrowthRate === 'number'
                      ? pop.averageAnnualGrowthRate
                      : computeCagr(popData, popLabels)

    await nextTick()
    const popCtx = (document.getElementById('popChart') as HTMLCanvasElement)?.getContext('2d')
    if (popCtx && popLabels.length) {
      popChart = new Chart(popCtx, {
        type: 'line',
        data: {
          labels: popLabels,
          datasets: [{ label: 'CBD Population', data: popData, tension: 0.2, pointRadius: 2 }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { ticks: { callback: (v) => Number(v).toLocaleString() } }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.parsed.y).toLocaleString()}`
              }
            }
          }
        }
      })
    }

    // ----- Vehicles (Victoria) -----
    const veh = await apiGet(`/insights/carOwnership?startYear=${startYear.value}&endYear=${endYear.value}`)
    // Accept multiple shapes from backend
    let vehLabels: (number|string)[] = []
    let vehVals: number[] = []

    if (Array.isArray(veh.items)) {
      vehLabels = veh.items.map((x:any)=> x.ref_year ?? x.year)
      vehVals   = veh.items.map((x:any)=> Number(x.total ?? x.vehicle_count ?? x.count ?? 0))
    } else if (Array.isArray(veh.years) && Array.isArray(veh.vehicleCounts)) {
      vehLabels = veh.years
      vehVals   = veh.vehicleCounts.map((n:any)=> Number(n ?? 0))
    } else if (Array.isArray(veh.values) && Array.isArray(veh.labels)) {
      vehLabels = veh.labels
      vehVals   = veh.values.map((n:any)=> Number(n ?? 0))
    } else {
      // fallback: show zeroed series for selected range
      vehLabels = years(startYear.value, endYear.value)
      vehVals   = vehLabels.map(()=>0)
    }

    vehCagr.value = typeof veh.cagrPct === 'number'
      ? veh.cagrPct
      : computeCagr(vehVals, vehLabels)

    await nextTick()
    const vehCtx = (document.getElementById('vehChart') as HTMLCanvasElement)?.getContext('2d')
    if (vehCtx && vehLabels.length) {
      vehChart = new Chart(vehCtx, {
        type: 'bar',
        data: {
          labels: vehLabels.map(String),
          datasets: [{ label: 'Registered vehicles', data: vehVals, borderWidth: 1 }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { title: { display: true, text: 'Year' } },
            y: {
              title: { display: true, text: 'Vehicles' },
              ticks: { callback: (v) => Number(v).toLocaleString() }
            }
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.parsed.y).toLocaleString()}`
              }
            }
          }
        }
      })
    }

  } catch (e:any) {
    error.value = e?.message ?? String(e)
    destroyCharts()
  } finally {
    loading.value = false
  }
}

function refresh() {
  if (Number.isFinite(startYear.value) && Number.isFinite(endYear.value)) draw()
}

onMounted(draw)
onBeforeUnmount(destroyCharts)
watch([startYear, endYear], draw)
</script>

<style scoped>
.controls{display:flex; gap:.75rem; align-items:end; margin-bottom:.5rem}
.controls label{display:flex; flex-direction:column; gap:.25rem}
.controls input{border:1px solid #ddd; border-radius:8px; padding:.4rem .6rem; width:7rem}
.controls button{padding:.45rem .8rem; border-radius:8px; background:black; color:#fff}
.err{color:#b91c1c; font-size:.9rem}
.meta{font-size:.85rem; opacity:.8; margin-top:.5rem}
.chart{height:300px} /* important: gives the canvas a real height */
</style>
