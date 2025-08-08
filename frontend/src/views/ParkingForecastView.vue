<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { fetchJSON } from '../services/api';
type Item = { place:string; inMins:number; expectedAvailable:number; confidence:number };
const items = ref<Item[]>([]);
onMounted(async () => items.value = await fetchJSON<Item[]>('/mock/forecast.json'));
</script>

<template>
  <h1>Parking Forecast</h1>
  <div v-for="it in items" :key="it.place" style="border:1px solid #eee;padding:12px;margin:8px 0;border-radius:8px;">
    <b>{{ it.place }}</b> — in {{ it.inMins }} mins:
    <span>expected {{ it.expectedAvailable }} spots</span>
    <span style="margin-left:8px;">confidence {{ Math.round(it.confidence*100) }}%</span>
  </div>
</template>
