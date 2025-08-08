<template>
  <form class="row card" @submit.prevent="onSubmit">
    <input class="input" v-model="q" :placeholder="placeholder ?? 'Enter address…'" />
    <button class="btn" type="submit">Search</button>
  </form>
</template>
<script setup lang="ts">
import { ref } from 'vue';
const props = defineProps<{ placeholder?:string }>();
const emit = defineEmits<{(e:'search', value:string):void}>();
const q = ref('');
function onSubmit(){ if(q.value.trim()) emit('search', q.value.trim()); }
</script>
