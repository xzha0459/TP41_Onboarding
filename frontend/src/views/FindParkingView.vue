<template>
  <section class="container">
    <h1>Find Parking</h1>

    <form class="form" @submit.prevent="onSubmit">
      <input class="input" v-model="address" placeholder="Enter address…" />
      <input class="input" v-model.number="maxWalk" type="number" min="1" step="1" />
      <button class="btn" :disabled="loading">Search</button>
    </form>

    <p v-if="loading">Loading…</p>
    <p v-else-if="error" class="error">{{ error }}</p>

    <ul v-else>
      <li v-for="p in results" :key="p.kerbside_id">
        <strong>{{ p.zone_number }}</strong> · {{ p.status_description }}
        · {{ (p.distance_km).toFixed(2) }} km · walk {{ p.walk_time }} min
      </li>
      <li v-if="!results.length && searched">No results.</li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { fetchNearby, type NearbyItem } from "@/services/api";
import axios from "axios";

const address = ref("");
const maxWalk = ref(5);
const loading = ref(false);
const error = ref("");
const searched = ref(false);
const results = ref<NearbyItem[]>([]);


function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data
      ? (typeof err.response.data === "string"
        ? err.response.data
        : JSON.stringify(err.response.data))
      : "";
    return `Request failed (${err.response?.status ?? ""}) ${detail}`;
  }
  if (err instanceof Error) return err.message;
  return "Request failed";
}

async function onSubmit() {
  loading.value = true; error.value = ""; searched.value = true;
  try {
    const body: { address: string; max_walk_time?: number } = {
      address: address.value.trim(),
    };
    if (Number(maxWalk.value) && Number(maxWalk.value) !== 5) {
      body.max_walk_time = Number(maxWalk.value);
    }
    results.value = await fetchNearby(body);
  } catch (err: unknown) {
    error.value = getErrorMessage(err);
  } finally {
    loading.value = false;
  }
}

</script>

<style scoped>
.container { max-width: 820px; margin: 0 auto; padding: 16px; }
.form { display: grid; grid-template-columns: 1fr 160px 120px; gap: 8px; }
.input { padding: 8px; border: 1px solid #ddd; border-radius: 6px; }
.btn { padding: 8px 12px; border: 0; border-radius: 8px; cursor: pointer; }
.error { color: #c00; }
</style>
