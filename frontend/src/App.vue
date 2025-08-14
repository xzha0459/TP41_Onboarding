<template>
  <div id="app">
    <!-- NAVBAR -->
    <header class="site-header">
      <div class="container row header-inner">
        <div class="brand row">
          <span class="logo-dot" aria-hidden="true"></span>
          <strong class="brand-name">ParkSmart Melb</strong>
        </div>

        <nav class="nav row">
          <router-link class="nav-link" to="/find">Find Parking</router-link>
          <router-link class="nav-link" to="/insights">Insights</router-link>
          <router-link class="nav-link" to="/forecast">Parking Forecast</router-link>
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

<script setup lang="ts"></script>

<style scoped>
/* ===== 头部：去透明，整条纯白 ===== */
.site-header{
  position: sticky; top: 0; z-index: 1000;
  background-color: #ffffff;          /* 纯白实心 */
  border-bottom: 1px solid rgba(0,0,0,.06);
  box-shadow: 0 4px 24px rgba(0,0,0,0.05);
  /* 防止任何背景混合/模糊效果影响 */
  -webkit-backdrop-filter: none;
  backdrop-filter: none;
  isolation: isolate;                 /* 避免与下方元素产生混合导致发灰/发亮 */
}

.header-inner{
  justify-content: space-between;
  align-items: center;
  padding: 18px 0;
}

.brand{ gap: 10px; align-items: center; }
.logo-dot{
  width: 28px; height: 28px; border-radius: 50%;
  display: inline-block;
  background: radial-gradient(circle at 30% 30%, #94b3ff 0%, #5b7cff 60%, #3651f3 100%);
  box-shadow: 0 6px 14px rgba(54,81,243,.35);
}
.brand-name{
  font-size: 18px;
  letter-spacing: .2px;
  color: #1f2937;
  font-weight: 700;
}

.nav{ gap: 22px; align-items: center; }
.nav-link{
  /* 去掉大写，显示真实标题 */
  font-size: 14px;
  letter-spacing: .2px;
  color: #475569;
  text-decoration: none;
  padding: 8px 2px;
  transition: color .15s ease, opacity .15s ease;
}
.nav-link.router-link-active{ color: #1f2937; }
.nav-link:hover{ color:#111827; opacity: .9; }

/* 下面保持你原来的主体样式 */
.main-panel-wrapper {
  padding: 40px 20px;
  min-height: calc(100vh - 60px);
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
.main-panel .container { max-width: none; padding: 20px 40px; }

@media (max-width: 768px) {
  .header-inner{ padding: 14px 0; }
  .nav{ gap: 14px; }
  .main-panel-wrapper { padding: 20px 16px; }
  .main-panel .container { padding: 20px 24px; }
}
</style>
