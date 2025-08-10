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
  q.value = '';
}
</script>
