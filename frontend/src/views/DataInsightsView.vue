<template>
  <div class="p-6 space-y-6 data-insights">
    <!-- Header -->
    <header class="space-y-2">
      <h1 class="text-2xl font-semibold">Data Insights</h1>
      <p class="text-sm opacity-80">
        CBD population & vehicle registrations — placeholders for now (choose dates below)
      </p>
    </header>

    <!-- Controls -->
    <div class="flex flex-wrap items-end gap-4">
      <label class="flex flex-col">
        <span class="text-xs uppercase tracking-wide">Start Year</span>
        <input
          type="number"
          v-model.number="startYear"
          min="2001"
          max="2025"
          class="border rounded px-3 py-2 w-32"
        />
      </label>

      <label class="flex flex-col">
        <span class="text-xs uppercase tracking-wide">End Year</span>
        <input
          type="number"
          v-model.number="endYear"
          min="2001"
          max="2025"
          class="border rounded px-3 py-2 w-32"
        />
      </label>

      <button @click="refresh" class="px-4 py-2 rounded bg-black text-white hover:opacity-90">
        Refresh
      </button>

      <span v-if="loading" class="text-sm">Loading…</span>
      <span v-if="error" class="text-sm text-red-600">{{ error }}</span>
    </div>

    <!-- Sections with placeholders -->
    <Section title="Population–Traffic Analysis">
      <div
        style="height:280px;display:grid;place-items:center;color:var(--muted);text-align:center;padding:0 12px;"
      >
        <div>
          <div class="text-sm">Chart placeholder</div>
          <div class="text-xs opacity-70 mt-1">
            CBD Population • {{ startYear }}–{{ endYear }}<br />
            (We’ll render the live chart here once endpoints are ready)
          </div>
        </div>
      </div>
    </Section>

    <Section title="Car Ownership Trend">
      <div
        style="height:220px;display:grid;place-items:center;color:var(--muted);text-align:center;padding:0 12px;"
      >
        <div>
          <div class="text-sm">Chart placeholder</div>
          <div class="text-xs opacity-70 mt-1">
            Vehicle Registration Growth (VIC) • {{ startYear }}–{{ endYear }}<br />
            (Placeholder only — wiring comes next)
          </div>
        </div>
      </div>
    </Section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Section from '../components/BaseSection.vue'

const startYear = ref(2016)
const endYear = ref(2021)
const loading = ref(false)
const error = ref<string | null>(null)

function refresh() {
  // Placeholder: keep UI responsive. Hook API calls here later.
  loading.value = true
  setTimeout(() => {
    loading.value = false
    error.value = null
  }, 200)
}
</script>

<style scoped>
.data-insights { font-family: system-ui, -apple-system, Segoe UI, Roboto, Inter, Arial, sans-serif; }
</style>
