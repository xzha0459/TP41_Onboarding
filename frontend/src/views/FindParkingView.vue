<script setup lang="ts">
import Section from '../components/BaseSection.vue';
import SearchBar from '../components/SearchBar.vue';
import ParkingCard from '../components/ParkingCard.vue';

const results = [
  { name:'Sample Car Park A', distanceKm:0.85, walkMins:11 },
  { name:'Sample Car Park B', distanceKm:1.20, walkMins:16 }
];

function handleSearch(q:string){
  // 现在先不调接口：只做 UI 流程
  console.log('search:', q);
}
</script>

<template>
  <Section title="Find Parking">
    <SearchBar placeholder="e.g. 3000 VIC or Melbourne Central" @search="handleSearch" />
    <div class="grid cards" style="margin-top:10px">
      <ParkingCard v-for="r in results" :key="r.name" v-bind="r" />
    </div>
  </Section>

  <Section title="Map (placeholder)">
    <div style="height:360px;border:1px dashed var(--border);border-radius:var(--radius);display:grid;place-items:center;color:var(--muted)">
      Map goes here
    </div>
  </Section>
</template>
