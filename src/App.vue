<template>
  <div id="app">
    <header>
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/parking">Parking Finder</RouterLink>
        <RouterLink to="/insights">Data Insights</RouterLink>
        <RouterLink to="/eco">Eco Commute</RouterLink>
      </nav>
    </header>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  color: #2c3e50;
}

nav {
  padding: 20px;
  background: #f8f9fa;
  display: flex;
  gap: 20px;
}

nav a {
  text-decoration: none;
  color: #007bff;
  padding: 8px 16px;
  border-radius: 4px;
}

nav a:hover {
  background: #e9ecef;
}

nav a.router-link-active {
  background: #007bff;
  color: white;
}

main {
  padding: 20px;
}
</style>
