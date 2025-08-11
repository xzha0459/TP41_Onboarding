<template>
  <div class="p-6 space-y-6">
    <header class="space-y-1">
      <h1 class="text-2xl font-semibold">Parking History</h1>
      <p class="text-sm opacity-80">Pick a street segment and date window to see trends.</p>
    </header>

    <!-- Controls -->
    <section class="grid gap-4 md:grid-cols-[1fr,auto,auto,auto] items-end">
      <label class="flex flex-col gap-1">
        <span class="text-xs uppercase tracking-wide">Segment</span>
        <div class="flex gap-2">
          <select v-model="segmentId" class="border rounded px-3 py-2 min-w-[220px]">
            <option v-for="s in topSegments" :key="s.segment_id" :value="s.segment_id">
              {{ s.segment_id }} — {{ s.samples }} samples
            </option>
          </select>
          <button class="px-3 py-2 rounded border" @click="loadTopSegments" :disabled="loading">Refresh list</button>
        </div>
        <small class="opacity-70">List shows busiest segments within the chosen dates below.</small>
      </label>

      <label class="flex flex-col gap-1">
        <span class="text-xs uppercase tracking-wide">Start</span>
        <input type="date" v-model="startDate" class="border rounded px-3 py-2" />
      </label>

      <label class="flex flex-col gap-1">
        <span class="text-xs uppercase tracking-wide">End</span>
        <input type="date" v-model="endDate" class="border rounded px-3 py-2" />
      </label>

      <button class="px-4 py-2 rounded bg-black text-white hover:opacity-90" @click="refresh" :disabled="loading">
        {{ loading ? 'Loading…' : 'View history' }}
      </button>
    </section>

    <div v-if="error" class="text-red-600 text-sm">{{ error }}</div>
    <div v-if="hint" class="text-amber-700 text-sm">{{ hint }}</div>

    <!-- Hourly line -->
    <Section title="Hourly free ratio (selected window)">
      <div class="chart">
        <canvas id="histChart"/>
      </div>
      <div class="text-xs opacity-70 mt-2" v-if="summary">
        {{ summary.count }} hourly buckets. {{ summary.start }} → {{ summary.end }}
      </div>
    </Section>

    <!-- Heatmap + windows -->
    <Section title="Weekly pattern (7×24) & best arrival windows">
      <div class="grid md:grid-cols-[1fr,280px] gap-6">
        <!-- Heatmap -->
        <div class="overflow-x-auto">
          <table class="heatmap w-full min-w-[640px] border-collapse">
            <thead>
              <tr>
                <th></th>
                <th v-for="h in 24" :key="h" class="text-xs font-normal">{{ (h-1).toString().padStart(2,'0') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(day, d) in dayLabels" :key="day">
                <th class="text-xs text-left font-normal pr-2">{{ day }}</th>
                <td v-for="h in 24" :key="h">
                  <div
                    class="cell"
                    :title="cellTitle(d, h-1)"
                    :style="cellStyle(d, h-1)"
                  ></div>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="text-xs opacity-70 mt-2">Color = % free (darker = better). Empty = no samples or below threshold.</div>
        </div>

        <!-- Best windows -->
        <div class="space-y-2">
          <h3 class="font-medium">Suggested arrival windows</h3>
          <div v-if="windows.length === 0" class="text-sm opacity-70">No windows with enough samples.</div>
          <ul class="space-y-2">
            <li v-for="w in windows" :key="w.dow + '-' + w.hour" class="border rounded p-2 flex items-center justify-between">
              <span>{{ dayLabels[w.dow] }} @ {{ w.hour.toString().padStart(2,'0') }}:00</span>
              <span class="text-sm opacity-80">{{ Math.round(w.avg_free_ratio*100) }}% free</span>
            </li>
          </ul>
        </div>
      </div>
    </Section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import Section from '../components/BaseSection.vue'
import { getTopSegments, getHistoryBySegment, getSummaryBySegment } from '../services/api'

Chart.register(...registerables)

const loading = ref(false)
const error = ref<string | null>(null)
const hint = ref<string | null>(null)

const today = new Date()
const defaultEnd = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()))
const defaultStart = new Date(defaultEnd); defaultStart.setUTCMonth(defaultStart.getUTCMonth() - 2)

function fmt(d: Date) {
  // yyyy-mm-dd
  return d.toISOString().slice(0,10)
}

const startDate = ref(fmt(defaultStart))     // e.g. 2025-06-11
const endDate = ref(fmt(defaultEnd))         // today (UTC)
const topSegments = ref<Array<{segment_id:string; samples:number}>>([])
const segmentId = ref<string>('')

let histChart: Chart | null = null
const historyItems = ref<Array<{ timestamp:string; free_ratio:number|null; samples:number }>>([])
const summary = ref<any>(null)
const heatmap = ref<Array<{ dow:number; hh:number; samples:number; avg_free_ratio:number }>>([])
const windows = ref<Array<{ dow:number; hour:number; avg_free_ratio:number }>>([])

const dayLabels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'] // matches 0..6 mapping in backend

function destroyCharts() { if (histChart) { histChart.destroy(); histChart = null } }

async function loadTopSegments() {
  loading.value = true; error.value = null; hint.value = null
  try {
    const j = await getTopSegments(startDate.value, endDate.value, 10)
    topSegments.value = j.items
    if (!segmentId.value && j.items.length) segmentId.value = j.items[0].segment_id
  } catch (e:any) {
    error.value = e?.message ?? String(e)
  } finally {
    loading.value = false
  }
}

async function refresh() {
  if (!segmentId.value) { error.value = 'Pick a segment.'; return }
  loading.value = true; error.value = null; hint.value = null
  try {
    // Hourly
    const h = await getHistoryBySegment(segmentId.value, startDate.value, endDate.value)
    historyItems.value = h.items ?? []
    summary.value = h.summary ?? null
    hint.value = h.hint ?? null

    // Chart
    destroyCharts()
    const ctx = (document.getElementById('histChart') as HTMLCanvasElement).getContext('2d')!
    histChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: historyItems.value.map(x => x.timestamp),
        datasets: [{
          label: '% free',
          data: historyItems.value.map(x => x.free_ratio == null ? null : Math.round(x.free_ratio * 100)),
          spanGaps: true,
          tension: 0.2,
          pointRadius: 2,
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, scales: { y: { suggestedMin: 0, suggestedMax: 100 } } }
    })

    // Heatmap + windows
    const s = await getSummaryBySegment(segmentId.value, startDate.value, endDate.value, 3, 5)
    heatmap.value = s.heatmap ?? []
    windows.value = s.windows ?? []
    if (s.hint && !hint.value) hint.value = s.hint
  } catch (e:any) {
    error.value = e?.message ?? String(e)
    destroyCharts()
  } finally {
    loading.value = false
  }
}

function cell(dow:number, hh:number) {
  return heatmap.value.find(b => b.dow === dow && b.hh === hh)
}
function cellTitle(dow:number, hh:number) {
  const b = cell(dow, hh)
  if (!b) return `${dayLabels[dow]} ${hh.toString().padStart(2,'0')}:00 — no data`
  return `${dayLabels[dow]} ${hh.toString().padStart(2,'0')}:00 — ${Math.round(b.avg_free_ratio*100)}% free (${b.samples} samples)`
}
function cellStyle(dow:number, hh:number) {
  const b = cell(dow, hh)
  if (!b || b.samples === 0) return { background: '#eee' }
  const pct = Math.round(b.avg_free_ratio * 100) // 0..100
  // green scale: 0% -> very light, 100% -> dark
  const light = 95 - Math.round(pct * 0.6) // 95..35
  return { background: `hsl(140 60% ${light}%)` }
}

onMounted(async () => {
  await loadTopSegments()
  if (segmentId.value) await refresh()
})
watch([startDate, endDate], () => { /* auto-refresh list when date window changes */ loadTopSegments() })
</script>

<style scoped>
.chart { height: 280px; }
.heatmap th, .heatmap td { padding: 2px; }
.cell { width: 22px; height: 22px; border-radius: 4px; }
</style>
