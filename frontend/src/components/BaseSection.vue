<template>
  <section class="card" style="margin-bottom:12px">
    <header class="row" style="justify-content:space-between;margin-bottom:8px">
      <h2 class="h1">{{ title }}</h2>
      <slot name="actions" />
    </header>
    <slot />
  </section>
</template>
<script setup lang="ts">
defineProps<{ title:string }>();
</script>
