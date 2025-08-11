<template>
  <div class="insights-panel">
    <div class="filters">
      <label>State
        <select v-model="stateCode">
          <option>VIC</option><option>NSW</option><option>QLD</option>
          <option>WA</option><option>SA</option><option>TAS</option>
          <option>ACT</option><option>NT</option>
        </select>
      </label>

      <label>Region ID
        <input v-model="regionId" placeholder="CBD_MEL" />
      </label>

      <label>Start
        <input type="number" v-model.number="startYear" min="1990" />
      </label>

      <label>End
        <input type="number" v-model.number="endYear" min="1990" />
      </label>

      <button @click="load" :disabled="loading">Refresh</button>
    </div>

    <p v-if="loading">Loading insights…</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="!loading && !error" class="grid">
      <div class="card">
        <h3>📈 Car ownership — {{ stateCode }}</h3>
        <p>AAGR: <strong>{{ car?.averageAnnualGrowthRate?.toFixed(2) }}%</strong></p>
        <ul>
          <li v-for="p in car?.values" :key="'car-'+p.year">
            <strong>{{ p.year }}</strong> — {{ p.value.toLocaleString() }} vehicles
          </li>
        </ul>
        <h4 v-if="car?.vehiclesPer1000">Per 1k people</h4>
        <ul v-if="car?.vehiclesPer1000">
          <li v-for="p in car!.vehiclesPer1000!" :key="'v1k-'+p.year">
            <strong>{{ p.year }}</strong> — {{ p.value }}
          </li>
        </ul>
      </div>

      <div class="card">
        <h3>CBD population</h3>
        <p>AAGR: <strong>{{ pop?.averageAnnualGrowthRate?.toFixed(2) }}%</strong></p>
        <ul>
          <li v-for="p in pop?.values" :key="'pop-'+p.year">
            <strong>{{ p.year }}</strong> — {{ p.value.toLocaleString() }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { CarOwnershipResp, CbdPopulationResp } from '@/services/insight'
import { insightsApi } from '@/services/insight'

const loading = ref(false)
const error = ref<string | null>(null)

const stateCode = ref<'VIC'|'NSW'|'QLD'|'WA'|'SA'|'TAS'|'ACT'|'NT'>('VIC')
const regionId = ref('CBD_MEL')
const startYear = ref<number | undefined>(2010)
const endYear = ref<number | undefined>(2024)

const car = ref<CarOwnershipResp | null>(null)
const pop = ref<CbdPopulationResp | null>(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    const [carResp, popResp] = await Promise.all([
      insightsApi.carOwnership(stateCode.value, startYear.value, endYear.value),
      insightsApi.cbdPopulation(regionId.value, startYear.value, endYear.value),
    ])
    car.value = carResp
    pop.value = popResp
  } catch (e: any) {
    error.value = e?.message ?? 'Failed to load insights'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.insights-panel { display: grid; gap: 16px; }
.filters { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; background:#f6f6f6; padding:12px; border-radius:12px; }
.grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
.card { border: 1px solid #e7e7e7; border-radius: 12px; padding: 12px; background: #fff; }
.error { color: #c00; }
</style>
