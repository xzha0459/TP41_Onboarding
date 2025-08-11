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

const props = defineProps<{ markers: MarkerInput[] }>();

const mapEl = ref<HTMLDivElement | null>(null);
let map: google.maps.Map | null = null;
let gmarkers: google.maps.Marker[] = [];

function getGoogleIcon(occupied?: boolean, probability?: number) {

  if (probability != null) {
    const p = probability > 1 ? probability / 100 : probability;
    if (p >= 0.5) return 'http://maps.google.com/mapfiles/ms/icons/green-dot.png';
    if (p >= 0.4) return 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png';
    return 'http://maps.google.com/mapfiles/ms/icons/red-dot.png';
  }


  if (occupied != null) {
    return occupied
      ? 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
      : 'http://maps.google.com/mapfiles/ms/icons/green-dot.png';
  }


  return 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png';
}

function render() {
  if (!map) return;


  gmarkers.forEach((m) => m.setMap(null));
  gmarkers = [];

  const bounds = new google.maps.LatLngBounds();

  for (const m of props.markers) {
    const pos = { lat: m.lat, lng: m.lng };
    bounds.extend(pos);

    const marker = new google.maps.Marker({
      position: pos,
      map,
      icon: getGoogleIcon(m.occupied, m.probability),
      title: m.label,
    });


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
