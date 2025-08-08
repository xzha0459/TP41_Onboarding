<template>
  <header style="position:sticky;top:0;z-index:10;background:rgba(11,12,16,.9);backdrop-filter:saturate(1.2) blur(6px);border-bottom:1px solid var(--border);">
    <div class="container row" style="justify-content:space-between;">
      <div class="row" style="gap:10px">
        <strong>Melbourne Parking</strong>
        <span class="muted">| v0.1</span>
      </div>
      <nav class="row" style="gap:14px">
        <router-link to="/find">Find Parking</router-link>
        <router-link to="/insights">Insights</router-link>
        <router-link to="/history">History</router-link>
        <router-link to="/forecast">Forecast</router-link>
        <router-link to="/green">Green</router-link>
      </nav>
    </div>
  </header>

  <main class="container" style="padding-block:18px;">
    <router-view />
  </main>
</template>

