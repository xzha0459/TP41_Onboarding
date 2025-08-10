<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { fetchJSON } from '../services/api';

type Slot = { time:string; prob:number };
type Forecast = { placeId:number; placeName:string; slots:Slot[] };
type Lot = { id:number; name:string };

const lots = ref<Lot[]>([]);
const data = ref<Forecast[]>([]);

// Selectors
const placeId = ref<number|null>(null);
const date = ref<string>(''); // yyyy-mm-dd
const time = ref<string>(''); // HH:mm

// Display result
const result = ref<{ placeName:string; when:string; prob:number } | null>(null);

// Load lot list & forecast data (mock)
onMounted(async () => {
  const rawLots = await fetchJSON<any[]>('/mock/parking.json');
  lots.value = rawLots.map(r => ({ id: r.id, name: r.name }));
  if (lots.value.length) placeId.value = lots.value[0].id;

  data.value = await fetchJSON<Forecast[]>('/mock/forecast.json');
});

// Find nearest slot to the selected time
function nearestSlot(slots: Slot[], iso: string): Slot | null {
  const target = new Date(iso).getTime();
  let best: Slot | null = null, diff = Infinity;
  for (const s of slots) {
    const t = new Date(s.time).getTime();
    const d = Math.abs(t - target);
    if (d < diff) { diff = d; best = s; }
  }
  return best;
}

function onCheck() {
  if (!placeId.value || !date.value || !time.value) { alert('Please select location, date, and time'); return; }
  const iso = new Date(`${date.value}T${time.value}:00`).toISOString();
  const f = data.value.find(d => d.placeId === placeId.value);
  if (!f || !f.slots?.length) { result.value = null; return; }
  const slot = nearestSlot(f.slots, iso);
  if (!slot) { result.value = null; return; }
  result.value = { placeName: f.placeName, when: iso, prob: slot.prob };
}

// Colors for probability bar
const percent = computed(() => result.value ? Math.round(result.value.prob * 100) : 0);
function badgeColor(p:number){ return p>=70?'#2e7d32':p>=40?'#f9a825':'#c62828'; } // green / yellow / red
</script>

<template>
  <h1>Parking Forecast</h1>

  <!-- Selectors -->
  <div class="card" style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px">
    <select class="input" style="max-width:260px" v-model.number="placeId">
      <option v-for="l in lots" :key="l.id" :value="l.id">{{ l.name }}</option>
    </select>
    <input class="input" type="date" v-model="date" style="max-width:170px">
    <input class="input" type="time" v-model="time" style="max-width:140px" step="1800">
    <button class="btn" @click="onCheck">Check</button>
  </div>

  <!-- Result -->
  <div v-if="result" class="card" style="display:flex;justify-content:space-between;align-items:center">
    <div>
      <div style="font-weight:600">{{ result.placeName }}</div>
      <div class="muted">Time: {{ new Date(result.when).toLocaleString() }}</div>
      <div class="muted">Probability of availability</div>
    </div>
    <div style="min-width:220px">
      <div style="height:10px;border:1px solid var(--border);border-radius:999px;overflow:hidden;margin-bottom:6px;">
        <div :style="{width: percent+'%', height:'100%', background: badgeColor(percent)}"></div>
      </div>
      <div style="text-align:right;font-weight:700">{{ percent }}%</div>
    </div>
  </div>

  <p v-else class="muted">Select a location, date, and time, then click <b>Check</b> to see the probability of availability.</p>
</template>
