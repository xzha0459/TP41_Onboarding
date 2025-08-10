<script setup lang="ts">
import { onMounted, ref } from 'vue';
import * as L from 'leaflet';
import SearchBar from '../components/SearchBar.vue';
import { fetchJSON } from '../services/api';


type Lot = { id:number; name:string; lat:number; lng:number; total?:number };
type Result = Lot & { distanceKm:number; walkMins:number };

const mapEl = ref<HTMLDivElement|null>(null);
let map: L.Map;
let userMarker: L.Marker | null = null;
const lots = ref<Lot[]>([]);
const results = ref<Result[]>([]);
const markersById = new Map<number, L.Marker>();

function haversine(lat1:number,lng1:number,lat2:number,lng2:number){
  const R=6371; const toRad=(d:number)=>d*Math.PI/180;
  const dLat=toRad(lat2-lat1), dLng=toRad(lng2-lng1);
  const a=Math.sin(dLat/2)**2 + Math.cos(toRad(lat1))*Math.cos(toRad(lat2))*Math.sin(dLng/2)**2;
  return 2*R*Math.asin(Math.sqrt(a));
}

// 地理编码（后端接 Google 后替换这里）
async function geocode(addr: string): Promise<{lat:number;lng:number} | null> {
  try {
    const url = `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(addr)}`;
    const r = await fetch(url);
    const data = await r.json();
    if (Array.isArray(data) && data.length) return { lat: +data[0].lat, lng: +data[0].lon };
  } catch {}
  return null;
}

// 🔌 把 SearchBar 的 @search 事件接进来
async function onSearch(query: string){
  const loc = await geocode(query);
  if (!loc) { alert('找不到这个地址，请更具体一些'); return; }

  // 定位地图 & 标注用户位置
  map.setView([loc.lat, loc.lng], 15);
  if (userMarker) userMarker.remove();
  userMarker = L.marker([loc.lat, loc.lng]).addTo(map).bindPopup('You are here').openPopup();

  // 计算距离/步行时间并排序
  results.value = lots.value
    .map(l => {
      const distanceKm = haversine(loc.lat, loc.lng, l.lat, l.lng);
      const walkMins = Math.round((distanceKm / 5) * 60);
      return { ...l, distanceKm, walkMins };
    })
    .sort((a,b)=>a.distanceKm-b.distanceKm)
    .slice(0, 8);

  // 滚到卡片区（可选）
  queueMicrotask(() => document.getElementById('nearby')?.scrollIntoView({behavior:'smooth'}));
}

onMounted(async () => {
  // 载入停车场假数据
  const raw = await fetchJSON<Array<any>>('/mock/parking.json');
  lots.value = raw.map(r => ({
    id: r.id, name: r.name,
    lat: typeof r.lat === 'string' ? parseFloat(r.lat) : r.lat,
    lng: typeof r.lng === 'string' ? parseFloat(r.lng) : (typeof r.lon === 'string' ? parseFloat(r.lon) : r.lng),
    total: r.total
  })).filter(x => Number.isFinite(x.lat) && Number.isFinite(x.lng));

  // 初始化地图
  map = L.map(mapEl.value!).setView([-37.8136, 144.9631], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(map);

  // 画停车点
  lots.value.forEach(l => {
    const icon = L.divIcon({ className: '', html: `<div style="width:12px;height:12px;border-radius:50%;background:#2e7d32;border:2px solid #333"></div>` });
    const m = L.marker([l.lat, l.lng], { icon }).addTo(map).bindPopup(`<b>${l.name}</b>`);
    markersById.set(l.id, m);
  });
});

// 点击卡片时，让地图飞到该点（可选）
function flyTo(id:number){
  const m = markersById.get(id);
  if (!m) return;
  map.flyTo(m.getLatLng(), 17);
  m.openPopup();
}
</script>

<template>
  <h1>Find Parking</h1>

  <!-- 用 SearchBar 触发搜索 -->
  <SearchBar placeholder="e.g. 3000 VIC or Melbourne Central" @search="onSearch" />

  <!-- 地图 -->
  <div ref="mapEl" style="height:360px;border:1px solid #2a2b33;border-radius:12px;margin:12px 0;"></div>

  <!-- 结果卡片 -->
  <section id="nearby" v-if="results.length">
    <h3 style="margin:8px 0;">Nearby car parks</h3>
    <div v-for="r in results" :key="r.id"
         @click="flyTo(r.id)"
         style="border:1px solid #2a2b33;border-radius:12px;padding:12px;margin:8px 0;cursor:pointer;">
      <div style="font-weight:600">{{ r.name }}</div>
      <div style="opacity:.8">{{ r.distanceKm.toFixed(2) }} km · Walking {{ r.walkMins }} mins</div>
    </div>
  </section>
  <p v-else style="opacity:.7">Enter the address and click "Search" to view nearby parking lots.</p>
</template>
