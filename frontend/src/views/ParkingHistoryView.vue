<template>
  <section class="container">
    <h1>Parking History</h1>

    <!-- 地址搜索 -->
    <SearchBar @search="onSearch" />

    <!-- 筛选控件 -->
    <div class="filters">
      <div class="filter-group">
        <label>Date Range:</label>
        <input v-model="startDate" type="date" class="date-input">
        <span>to</span>
        <input v-model="endDate" type="date" class="date-input">
      </div>

      <div class="filter-group">
        <label>Scope:</label>
        <select v-model="scope" class="scope-select">
          <option value="segment">Street Segment</option>
          <option value="bay">Individual Bay</option>
        </select>
      </div>

      <div class="actions">
        <button class="btn secondary" @click="clearFilters">Clear</button>
        <button class="btn primary" @click="toggleView">
          {{ viewMode === 'table' ? '🗺️ Map View' : '📋 Table View' }}
        </button>
      </div>
    </div>

    <!-- 地图视图 - 用于选择停车区域 -->
    <div v-if="viewMode === 'map'" class="map-section">
      <div class="map-header">
        <span v-if="nearbyResults.length">{{ nearbyResults.length }} parking areas found</span>
        <span v-else-if="searched">Click on a parking spot to view its history</span>
        <span v-else>Search for an address to see parking areas</span>
      </div>
      <GoogleParkingMap :markers="mapMarkers" @marker-click="onMarkerClick" />
    </div>

    <!-- 表格视图 - 显示历史数据 -->
    <div v-else class="table-section">
      <div v-if="!selectedArea" class="select-prompt">
        <p>📍 Please search for an address and select a parking area from the map to view history</p>
        <button class="btn primary" @click="viewMode = 'map'">Go to Map</button>
      </div>

      <div v-else-if="loading" class="loading">Loading history for {{ selectedArea.zone_number }}...</div>

      <div v-else-if="error" class="error">{{ error }}</div>

      <div v-else-if="historyData.length" class="table-view">
        <div class="table-header">
          <div class="area-info">
            <span class="area-title">{{ selectedArea.zone_number }} History</span>
            <span class="area-desc">{{ selectedArea.status_description }}</span>
          </div>
          <div class="table-actions">
            <span class="results-count">{{ historyData.length }} hourly records</span>
            <button class="btn small" @click="exportCSV">Export</button>
          </div>
        </div>

        <table class="history-table">
          <thead>
            <tr>
              <th @click="sortBy('timestamp')">Date & Time {{ getSortIcon('timestamp') }}</th>
              <th @click="sortBy('free_ratio')">Availability {{ getSortIcon('free_ratio') }}</th>
              <th @click="sortBy('samples')">Data Points {{ getSortIcon('samples') }}</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in paginatedRecords" :key="record.timestamp">
              <td>
                <div class="datetime">{{ formatDateTime(record.timestamp) }}</div>
                <div class="time-only">{{ formatTimeOnly(record.timestamp) }}</div>
              </td>
              <td>
                <span v-if="record.free_ratio !== null" class="ratio-badge" :class="getRatioClass(record.free_ratio)">
                  {{ Math.round(record.free_ratio * 100) }}%
                </span>
                <span v-else class="no-data">No data</span>
              </td>
              <td>
                <span class="samples-badge">{{ record.samples }}</span>
              </td>
              <td>
                <span v-if="record.free_ratio !== null" :class="getStatusClass(record.free_ratio)">
                  {{ getStatusText(record.free_ratio) }}
                </span>
                <span v-else class="status-unknown">Unknown</span>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="pagination">
          <button :disabled="currentPage === 1" @click="currentPage--">‹</button>
          <span>{{ currentPage }} / {{ totalPages }}</span>
          <button :disabled="currentPage === totalPages" @click="currentPage++">›</button>
        </div>
      </div>

      <div v-else-if="selectedArea" class="no-data">
        <p>No historical data found for {{ selectedArea.zone_number }}</p>
        <p class="hint">Try selecting a different date range</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import GoogleParkingMap from "@/components/maps/GoogleParkingMap.vue";
import SearchBar from "@/components/SearchBar.vue";
import { fetchNearby, type NearbyItem } from "@/services/api";

interface HistoryRecord {
  timestamp: string;
  free_ratio: number | null;
  samples: number;
}

// 响应式数据
const nearbyResults = ref<NearbyItem[]>([]);
const selectedArea = ref<NearbyItem | null>(null);
const historyData = ref<HistoryRecord[]>([]);
const loading = ref(false);
const error = ref('');
const searched = ref(false);

// 筛选参数
const scope = ref('segment');
const startDate = ref('');
const endDate = ref('');
const viewMode = ref<'table' | 'map'>('map');

// 排序和分页
const sortField = ref<keyof HistoryRecord>('timestamp');
const sortDirection = ref<'asc' | 'desc'>('desc');
const currentPage = ref(1);
const pageSize = 20;

// 搜索地址，获取附近停车区域
async function onSearch(address: string) {
  loading.value = true;
  error.value = '';
  searched.value = true;

  try {
    nearbyResults.value = await fetchNearby({ address });
    // 自动切换到地图视图显示结果
    viewMode.value = 'map';
  } catch (err: any) {
    error.value = err?.response?.data || err?.message || "Search failed";
    nearbyResults.value = [];
  } finally {
    loading.value = false;
  }
}

// 地图标记点击，选择停车区域
function onMarkerClick(marker: any, index: number) {
  selectedArea.value = nearbyResults.value[index];
  loadHistoryForArea();
}

// 从地图标记点击（需要地图组件支持）
async function loadHistoryForArea() {
  if (!selectedArea.value) return;

  loading.value = true;
  error.value = '';

  try {
    // 根据选择的区域获取历史数据
    const segmentId = scope.value === 'segment'
      ? extractSegmentId(selectedArea.value)
      : selectedArea.value.kerbside_id;

    const response = await fetchHistoryData({
      scope: scope.value,
      id: segmentId,
      startDate: startDate.value,
      endDate: endDate.value
    });

    historyData.value = response.items || response || [];
    currentPage.value = 1;

    // 自动切换到表格视图显示历史数据
    viewMode.value = 'table';
  } catch (err: any) {
    error.value = err?.message || "Failed to load history";
    historyData.value = [];
  } finally {
    loading.value = false;
  }
}

// 提取segment ID的辅助函数（可能需要根据实际数据调整）
function extractSegmentId(area: NearbyItem): string {
  // 这里可能需要根据你的数据结构调整
  // 假设segment_id可以从zone_number或其他字段推导
  return area.zone_number || area.kerbside_id;
}

// API调用函数
async function fetchHistoryData(params: {
  scope: string;
  id: string;
  startDate: string;
  endDate: string;
}) {
  const url = new URL('/parking/history', import.meta.env.VITE_API_BASE_URL || '');

  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      url.searchParams.append(key, String(value));
    }
  });

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

// 地图标记
const mapMarkers = computed(() =>
  nearbyResults.value.map(area => ({
    lat: area.latitude,
    lng: area.longitude,
    occupied: area.is_occupied,
    label: `${area.zone_number} • ${area.status_description}`,
  }))
);

// 排序和分页
const sortedData = computed(() => {
  const sorted = [...historyData.value];

  sorted.sort((a, b) => {
    let aValue = a[sortField.value];
    let bValue = b[sortField.value];

    if (sortField.value === 'timestamp') {
      aValue = new Date(aValue as string).getTime();
      bValue = new Date(bValue as string).getTime();
    }

    if (aValue === null && bValue === null) return 0;
    if (aValue === null) return 1;
    if (bValue === null) return -1;

    if (aValue < bValue) return sortDirection.value === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection.value === 'asc' ? 1 : -1;
    return 0;
  });

  return sorted;
});

const totalPages = computed(() => Math.ceil(sortedData.value.length / pageSize));

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return sortedData.value.slice(start, start + pageSize);
});

// 方法
function clearFilters() {
  startDate.value = '';
  endDate.value = '';
  selectedArea.value = null;
  historyData.value = [];
  nearbyResults.value = [];
  searched.value = false;
  error.value = '';
  currentPage.value = 1;
  viewMode.value = 'map';
}

function toggleView() {
  viewMode.value = viewMode.value === 'table' ? 'map' : 'table';
}

function sortBy(field: keyof HistoryRecord) {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortField.value = field;
    sortDirection.value = 'asc';
  }
  currentPage.value = 1;
}

function getSortIcon(field: keyof HistoryRecord) {
  if (sortField.value !== field) return '';
  return sortDirection.value === 'asc' ? '↑' : '↓';
}

function formatDateTime(timestamp: string) {
  return new Date(timestamp).toLocaleDateString('en-AU');
}

function formatTimeOnly(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString('en-AU', { hour: '2-digit', minute: '2-digit' });
}

function getRatioClass(ratio: number) {
  if (ratio >= 0.7) return 'high';
  if (ratio >= 0.3) return 'medium';
  return 'low';
}

function getStatusClass(ratio: number) {
  if (ratio >= 0.7) return 'status-good';
  if (ratio >= 0.3) return 'status-ok';
  return 'status-busy';
}

function getStatusText(ratio: number) {
  if (ratio >= 0.7) return 'Available';
  if (ratio >= 0.3) return 'Moderate';
  return 'Busy';
}

function exportCSV() {
  if (!selectedArea.value) return;

  const headers = ['Timestamp', 'Free Ratio (%)', 'Samples', 'Status'];
  const rows = sortedData.value.map(record => [
    record.timestamp,
    record.free_ratio !== null ? Math.round(record.free_ratio * 100) : 'N/A',
    record.samples,
    record.free_ratio !== null ? getStatusText(record.free_ratio) : 'Unknown'
  ]);

  const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `parking-history-${selectedArea.value.zone_number}-${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
}

// 初始化默认日期
onMounted(() => {
  const today = new Date();
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(today.getDate() - 30);

  endDate.value = today.toISOString().split('T')[0];
  startDate.value = thirtyDaysAgo.toISOString().split('T')[0];
});
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
}

h1 {
  margin-bottom: 20px;
  color: #1a1a1a;
}

.filters {
  background: #ffffff;
  border: 1px solid #e1e5e9;
  border-radius: 12px;
  padding: 16px;
  margin: 12px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 600;
  color: #1a1a1a;
  white-space: nowrap;
}

.date-input, .scope-select {
  padding: 6px 10px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: #ffffff;
  color: #1a1a1a;
}

.actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.primary {
  background: #0d6efd;
  color: white;
  border-color: #0d6efd;
}

.btn.primary:hover:not(:disabled) {
  background: #0b5ed7;
}

.btn.secondary {
  background: #6c757d;
  color: white;
  border-color: #6c757d;
}

.btn.secondary:hover {
  background: #5c636a;
}

.btn.small {
  padding: 6px 12px;
  font-size: 13px;
  background: white;
}

.btn.small:hover {
  background: #f8f9fa;
}

.map-section {
  background: #ffffff;
  border: 1px solid #e1e5e9;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
}

.map-header {
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e1e5e9;
  font-weight: 600;
  color: #1a1a1a;
}

.table-section {
  background: #ffffff;
  border: 1px solid #e1e5e9;
  border-radius: 12px;
  overflow: hidden;
}

.select-prompt {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #0d6efd;
}

.error {
  color: #dc3545;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 16px 20px;
  margin: 0;
}

.table-view {
  /* 继承父容器样式 */
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e1e5e9;
}

.area-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.area-title {
  font-weight: 600;
  color: #1a1a1a;
}

.area-desc {
  font-size: 14px;
  color: #6c757d;
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.results-count {
  font-size: 14px;
  color: #6c757d;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th {
  background: #f8f9fa;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid #e1e5e9;
  cursor: pointer;
  user-select: none;
}

.history-table th:hover {
  background: #e9ecef;
}

.history-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f8f9fa;
  vertical-align: top;
}

.history-table tr:hover {
  background: #f8f9fa;
}

.datetime {
  font-weight: 600;
  color: #1a1a1a;
}

.time-only {
  font-size: 12px;
  color: #6c757d;
}

.ratio-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.ratio-badge.high {
  background: #d1e7dd;
  color: #0f5132;
}

.ratio-badge.medium {
  background: #fff3cd;
  color: #664d03;
}

.ratio-badge.low {
  background: #f8d7da;
  color: #721c24;
}

.samples-badge {
  background: #e7f3ff;
  color: #0d6efd;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.no-data {
  color: #6c757d;
  font-style: italic;
}

.status-good {
  color: #198754;
  font-weight: 600;
}

.status-ok {
  color: #fd7e14;
  font-weight: 600;
}

.status-busy {
  color: #dc3545;
  font-weight: 600;
}

.status-unknown {
  color: #6c757d;
  font-style: italic;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #e1e5e9;
}

.pagination button {
  padding: 6px 10px;
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:hover:not(:disabled) {
  background: #f8f9fa;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.no-data .hint {
  font-size: 14px;
  margin-top: 8px;
}
</style>
