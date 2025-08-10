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
  occupied?: boolean;      // 列表页用
  probability?: number;    // 预测页用（0~1 或 0~100）
};

const props = defineProps<{ markers: MarkerInput[] }>();

const mapEl = ref<HTMLDivElement | null>(null);
let map: google.maps.Map | null = null;
let gmarkers: google.maps.Marker[] = [];

/** 概率上色（0~1 或 0~100 都行） */
function probColor(p?: number) {
  if (p == null) return "#2ecc71";
  const x = p > 1 ? p / 100 : p; // 归一化
  const r = Math.round(255 * (1 - x));
  const g = Math.round(255 * x);
  return `#${r.toString(16).padStart(2, "0")}${g
    .toString(16)
    .padStart(2, "0")}00`;
}

/** 自定义 SVG 图钉 —— 用 Symbol（Icon 没有 path，Symbol 才有） */
function svgPin(color: string): google.maps.Symbol {
  return {
    path:
      "M8 0C3.58 0 0 3.58 0 8c0 5.25 8 16 8 16s8-10.75 8-16C16 3.58 12.42 0 8 0z",
    fillColor: color,
    fillOpacity: 1,
    strokeColor: "#333",
    strokeWeight: 1,
    anchor: new google.maps.Point(8, 24),
    scale: 1.2,
  };
}

function render() {
  if (!map) return;

  // 清理旧标记
  gmarkers.forEach((m) => m.setMap(null));
  gmarkers = [];

  const bounds = new google.maps.LatLngBounds();

  for (const m of props.markers) {
    const pos = { lat: m.lat, lng: m.lng };
    bounds.extend(pos);

    const color =
      m.probability != null ? probColor(m.probability) : m.occupied ? "#d33" : "#2ecc71";

    const marker = new google.maps.Marker({
      position: pos,
      map,
      icon: svgPin(color),
      title: m.label,
    });

    // 黑色文本的 InfoWindow（内联 style）
    if (m.label) {
      const html = `<div style="max-width:240px;color:#000">${m.label}</div>`;
      const infowin = new google.maps.InfoWindow({ content: html });
      marker.addListener("click", () => infowin.open({ anchor: marker, map: map! }));
    }

    gmarkers.push(marker);
  }

  if (props.markers.length) {
    map.fitBounds(bounds, 32);
  }
}

async function init() {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string;
  const loader = new Loader({ apiKey, version: "weekly" });
  await loader.load();

  map = new google.maps.Map(mapEl.value as HTMLDivElement, {
    center: { lat: -37.8136, lng: 144.9631 }, // Melbourne fallback
    zoom: 13,
    mapTypeControl: false,
    streetViewControl: false,
  });

  render();
}

onMounted(init);
watch(() => props.markers, render, { deep: true });
</script>

<style scoped>
.map {
  width: 100%;
  height: 380px;
  border-radius: 12px;
  overflow: hidden;
}
</style>
