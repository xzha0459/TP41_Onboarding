<template>
  <form class="row card" @submit.prevent="onSubmit">
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
  // 移除了 q.value = ''; 这行，保留输入内容
}
</script>

<style scoped>
.row { display: flex; gap: 8px; }
.card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 12px; }
.input { flex: 1; padding: 8px; border: 1px solid #444; border-radius: 6px; background: #2a2a2a; color: #fff; }
.input:focus { border-color: #2ea44f; outline: none; }
.btn { padding: 8px 16px; border: none; border-radius: 6px; background: #2ea44f; color: white; cursor: pointer; }
.btn:hover { background: #2c974b; }
</style>
