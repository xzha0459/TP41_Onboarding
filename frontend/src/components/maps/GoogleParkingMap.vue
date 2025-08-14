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

type OriginInput = {
  latitude: number;
  longitude: number;
  address: string;
  formatted_address: string;
};

const props = defineProps<{
  markers: MarkerInput[];
  origin?: OriginInput | null;
}>();

const mapEl = ref<HTMLDivElement | null>(null);
let map: google.maps.Map | null = null;
let gmarkers: google.maps.Marker[] = [];
let originMarker: google.maps.Marker | null = null;

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

  // Clear existing parking markers
  gmarkers.forEach((m) => m.setMap(null));
  gmarkers = [];

  // Clear existing origin marker
  if (originMarker) {
    originMarker.setMap(null);
    originMarker = null;
  }

  const bounds = new google.maps.LatLngBounds();

  // Add origin marker if origin exists
  if (props.origin) {
    const originPos = { lat: props.origin.latitude, lng: props.origin.longitude };
    bounds.extend(originPos);

    originMarker = new google.maps.Marker({
      position: originPos,
      map,
      icon: 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png',
      title: props.origin.formatted_address || props.origin.address,
      zIndex: 1000, // Make sure origin marker is on top
    });

    // Add info window for origin
    const originInfoContent = `
      <div style="max-width:240px;color:#000">
        <strong>Search Location</strong><br>
        ${props.origin.formatted_address || props.origin.address}
      </div>
    `;
    const originInfoWindow = new google.maps.InfoWindow({ content: originInfoContent });
    originMarker.addListener("click", () => originInfoWindow.open({ anchor: originMarker!, map: map! }));
  }

  // Add parking markers
  for (const m of props.markers) {
    const pos = { lat: m.lat, lng: m.lng };
    bounds.extend(pos);

    const marker = new google.maps.Marker({
      position: pos,
      map,
      icon: getGoogleIcon(m.occupied, m.probability),
      title: m.label,
    });

    // Add info window for parking markers
    if (m.label) {
      const html = `<div style="max-width:240px;color:#000">${m.label}</div>`;
      const infowin = new google.maps.InfoWindow({ content: html });
      marker.addListener("click", () => infowin.open({ anchor: marker, map: map! }));
    }

    gmarkers.push(marker);
  }

  // Fit bounds if there are markers or origin
  if (props.markers.length || props.origin) {
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
watch(() => [props.markers, props.origin], render, { deep: true });
</script>

<style scoped>
.map {
  width: 100%;
  height: 380px;
  border-radius: 12px;
  overflow: hidden;
}
</style>
