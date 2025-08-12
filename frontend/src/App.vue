<template>
  <div id="app">
    <header style="position:sticky;top:0;z-index:10;background:rgba(255,255,255,0.95);backdrop-filter:saturate(1.2) blur(6px);border-bottom:1px solid var(--border);">
      <div class="container row" style="justify-content:space-between;">
        <div class="row" style="gap:10px">
          <strong>Melbourne Parking</strong>
        </div>
        <nav class="row" style="gap:14px">
          <router-link to="/find">Find Parking</router-link>
          <router-link to="/insights">Insights</router-link>
          <router-link to="/forecast">Forecast</router-link>
        </nav>
      </div>
    </header>

    <div class="main-panel-wrapper">
      <div class="main-panel">
        <main class="container" style="padding-block:18px;">
          <router-view />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.main-panel-wrapper {
  padding: 40px 20px;
  min-height: calc(100vh - 60px); /* 减去header高度 */
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.main-panel {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  width: 100%;
  max-width: 1400px;
  min-height: 600px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.main-panel .container {
  max-width: none;
  padding: 20px 40px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .main-panel-wrapper {
    padding: 20px 16px;
  }

  .main-panel .container {
    padding: 20px 24px;
  }
}
</style>
