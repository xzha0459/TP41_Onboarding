<template>
  <div class="legend-section">
    <h4 class="legend-title">Parking Code</h4>
    <div class="legend-grid">
      <div class="legend-item">
        <span class="legend-code">#P</span>
        <span class="legend-meaning">Max parking time in hours</span>
      </div>
      <div class="legend-item">
        <span class="legend-code">FP</span>
        <span class="legend-meaning">Free parking (minutes or hours)</span>
      </div>
      <div class="legend-item">
        <span class="legend-code">MP</span>
        <span class="legend-meaning">Metered (paid) parking</span>
      </div>
      <div class="legend-item">
        <span class="legend-code">DP2P</span>
        <span class="legend-meaning">Disabled parking (2 hours)</span>
      </div>
      <div class="legend-item">
        <span class="legend-code">HP</span>
        <span class="legend-meaning">Healthcare parking</span>
      </div>
      <div class="legend-item">
        <span class="legend-code">LZ</span>
        <span class="legend-meaning">Loading zone (15/30 mins)</span>
      </div>
      <div class="legend-item">
        <span class="legend-code">PP</span>
        <span class="legend-meaning">Permit-only parking</span>
      </div>
      <div class="legend-item">
        <span class="legend-code">QP</span>
        <span class="legend-meaning">Quick stop zone</span>
      </div>
      <div class="legend-item">
        <span class="legend-code">SP</span>
        <span class="legend-meaning">Special-purpose parking</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 这个组件不需要任何逻辑，纯展示组件
</script>

<style scoped>
.legend-section {
  margin: 0;
  padding: 0;
}

.legend-title {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

.legend-grid {
  display: grid;
  gap: 6px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-code {
  background: #f8f9fa;
  border: 1px solid #e1e5e9;
  border-radius: 4px;
  padding: 2px 6px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  color: #1a1a1a;
  min-width: 36px;
  text-align: center;
  flex-shrink: 0;
}

.legend-meaning {
  font-size: 12px;
  color: #6c757d;
  line-height: 1.3;
}

/* 当作为卡片使用时的样式调整 */
.legend-section.card-style {
  background: #f8f9fa;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 16px;
  margin: 0;
}

.legend-section.compact {
  margin: 0;
  padding: 0;
}

.legend-section.no-border {
  border-top: none;
  padding-top: 0;
  margin-top: 0;
}

/* 在FindParking页面中作为右侧卡片时的特殊样式 */
.legend-section {
  border-top: none;
  margin-top: 0;
  padding-top: 0;
}
</style>
