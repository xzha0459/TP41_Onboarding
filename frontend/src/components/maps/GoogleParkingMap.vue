<template>
  <div ref="mapEl" class="map"></div>
</template>

<script setup lang="ts">
import { Loader } from "@googlemaps/js-api-loader";
import { onMounted, ref, watch } from "vue";

type MarkerInput = {
  lat: number;
  lng: number;
  label?: string;
  occupied?: boolean;
  probability?: number;
};

/** ✅ 新增：接收搜索地址坐标（可选） */
const props = defineProps<{
  markers: MarkerInput[];
  origin?: { lat: number; lng: number } | null;
}>();

const mapEl = ref<HTMLDivElement | null>(null);
let map: google.maps.Map | null = null;

let gmarkers: google.maps.Marker[] = [];
/** ✅ 新增：保存搜索地址 marker 引用 */
let originMarker: google.maps.Marker | null = null;

/** 你的原本渲染逻辑：保持不变，仅用 props.markers */
function render() {
  if (!map) return;

  // 清除旧车位点
  for (const m of gmarkers) m.setMap(null);
  gmarkers = [];

  const bounds = new google.maps.LatLngBounds();

  for (const m of props.markers) {
    const marker = new google.maps.Marker({
      map: map!,
      position: { lat: m.lat, lng: m.lng },
      title: m.label,
    });

    // 这里保留你原来的 InfoWindow 等交互（颜色强制黑色，避免灰）
    if (m.label) {
      const html = `<div style="max-width:240px;color:#000">${m.label}</div>`;
      const infowin = new google.maps.InfoWindow({ content: html });
      marker.addListener("click", () => infowin.open({ anchor: marker, map: map! }));
    }

    gmarkers.push(marker);
    bounds.extend(marker.getPosition()!);
  }

  if (props.markers.length) {
    map.fitBounds(bounds, 32);
  }
}

/** ✅ 新增：单独渲染搜索地址的点，不影响其它 markers */
function renderOrigin() {
  if (!map) return;

  // 清理旧的搜索点
  if (originMarker) {
    originMarker.setMap(null);
    originMarker = null;
  }

  // 没有传 origin 就不画
  if (!props.origin) return;

  originMarker = new google.maps.Marker({
    map: map!,
    position: props.origin,
    title: "Searched address",
    icon: {
      path: google.maps.SymbolPath.CIRCLE,
      scale: 8,
      fillColor: "#1a73e8",
      fillOpacity: 1,
      strokeColor: "#ffffff",
      strokeWeight: 2,
    },
  });

  // 轻微移动视图到搜索点（不改变当前 zoom）
  map.panTo(props.origin);
}

/** 初始化地图：保持你的逻辑；仅在末尾多调一次 renderOrigin() */
async function init() {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || import.meta.env.VITE_GOOGLE_MAPS_API;
  const loader = new Loader({ apiKey, version: "weekly" });
  await loader.load();

  map = new google.maps.Map(mapEl.value as HTMLDivElement, {
    center: { lat: -37.8136, lng: 144.9631 }, // Melbourne fallback
    zoom: 13,
    mapTypeControl: false,
    streetViewControl: false,
  });

  render();
  renderOrigin(); // ✅ 新增：首次渲染搜索点
}

onMounted(init);
watch(() => props.markers, render, { deep: true });
/** ✅ 新增：监听 origin 变化，单独重画搜索点 */
watch(() => props.origin, renderOrigin, { deep: true });
</script>

<style scoped>
.map {
  width: 100%;
  height: 380px;
  border-radius: 12px;
  overflow: hidden;
}
</style>
