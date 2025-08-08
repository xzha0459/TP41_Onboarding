<template>
  <div class="card row" style="justify-content:space-between">
    <div>
      <div class="h3">{{ name }}</div>
      <div class="muted">{{ distanceKm.toFixed(2) }} km · walk ~ {{ walkMins }} mins</div>
    </div>
    <slot name="right" />
  </div>
</template>
<script setup lang="ts">
defineProps<{ name:string; distanceKm:number; walkMins:number }>();
</script>
