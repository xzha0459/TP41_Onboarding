<template>
  <div class="form">
    <input
      v-model="address"
      placeholder="Enter address..."
      class="address-input"
    />
    <input type="date" v-model="date" class="input">
    <input type="time" v-model="time" class="input">
    <input v-model.number="maxWalk" type="number" min="1" max="30" class="walk-input" placeholder="5">
    <button @click="onSubmit" :disabled="loading || !address.trim()" class="btn">Check</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const { loading } = defineProps<{ loading?: boolean }>();
const emit = defineEmits<{
  (e: 'search', data: { address: string; date: string; time: string; maxWalk: number }): void
}>();

const address = ref("");
const date = ref("");
const time = ref("");
const maxWalk = ref(5);

// 设置默认日期时间
onMounted(() => {
  const now = new Date();
  date.value = now.toISOString().split('T')[0];
  time.value = now.toTimeString().slice(0, 5);
});

function onSubmit() {
  if (!address.value) return;

  emit('search', {
    address: address.value,
    date: date.value,
    time: time.value,
    maxWalk: maxWalk.value
  });
}
</script>

<style scoped>
.form {
  display: flex;
  gap: 8px;
  margin: 16px 0;
  flex-wrap: wrap;
}

.address-input {
  flex: 1;
  min-width: 200px;
  padding: 8px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: #ffffff;
  color: #1a1a1a;
}

.input {
  padding: 8px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: #ffffff;
  color: #1a1a1a;
}

.walk-input {
  width: 60px;
  padding: 8px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: #ffffff;
  color: #1a1a1a;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: #0d6efd;
  color: white;
  cursor: pointer;
}

.btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}
</style>
