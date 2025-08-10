<template>
  <form class="row" @submit.prevent="onSubmit">
    <input
      class="input"
      v-model="q"
      :placeholder="placeholder ?? 'Enter address…'"
      autocomplete="off"
      aria-label="Search address"
    />
    <button class="btn" type="submit">Search</button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const { placeholder } = defineProps<{ placeholder?: string }>();
const emit = defineEmits<{ (e: 'search', value: string): void }>();

const q = ref('');

function onSubmit() {
  const v = q.value.trim();
  if (!v) return;
  emit('search', v);

}
</script>

<style scoped>
.row { display: flex; gap: 8px; }
.input { flex: 1; padding: 8px; border: 1px solid #e1e5e9; border-radius: 6px; background: #ffffff; color: #1a1a1a; }
.input:focus { border-color: #0d6efd; outline: none; box-shadow: 0 0 0 2px rgba(13,110,253,0.25); }
.btn { padding: 8px 16px; border: none; border-radius: 6px; background: #0d6efd; color: white; cursor: pointer; }
.btn:hover { background: #0b5ed7; }
</style>
