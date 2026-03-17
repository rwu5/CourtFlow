<template>
  <view class="vlist">
    <!-- Custom Nav -->
    <view class="vlist__nav">
      <view class="vlist__nav-inner">
        <text class="vlist__nav-title">场馆</text>
        <view class="vlist__search-btn" @tap="toggleSearch">
          <cf-icon name="search" :size="22" color="rgba(255,255,255,0.7)" />
        </view>
      </view>
      <!-- Search bar (expandable) -->
      <view v-if="showSearch" class="vlist__search-bar">
        <input
          v-model="searchQuery"
          class="vlist__search-input"
          placeholder="搜索场馆名称或地址"
          placeholder-class="vlist__search-placeholder"
          @input="onSearch"
        />
        <cf-icon name="close" :size="18" color="rgba(255,255,255,0.5)" @tap="clearSearch" />
      </view>
    </view>

    <!-- Filter chips -->
    <scroll-view class="vlist__filters-scroll" scroll-x>
      <view class="vlist__filters-row">
        <view
          v-for="f in filters"
          :key="f.key"
          class="vlist__filter-chip"
          :class="{ 'vlist__filter-chip--active': activeFilter === f.key }"
          @tap="setFilter(f.key)"
        >
          <text class="vlist__filter-text">{{ f.label }}</text>
        </view>
      </view>
    </scroll-view>

    <!-- Results header -->
    <view class="vlist__results-header">
      <text class="vlist__results-count">{{ filteredVenues.length }} 个场馆</text>
      <view class="vlist__sort-btn" @tap="toggleSort">
        <text class="vlist__sort-text">{{ sortLabel }}</text>
        <text class="vlist__sort-icon">⇅</text>
      </view>
    </view>

    <!-- Venue list -->
    <view v-if="!loading" class="vlist__list">
      <view
        v-for="v in filteredVenues"
        :key="v.id"
        class="vlist__card"
        @tap="goDetail(v.id)"
      >
        <!-- Photo -->
        <view class="vlist__card-img-wrap">
          <image class="vlist__card-img" :src="v.coverUrl" mode="aspectFill" />
          <view class="vlist__card-img-overlay" />
          <!-- Tags on image -->
          <view class="vlist__card-tags">
            <view class="vlist__card-tag" :class="v.isSelfOperated ? 'vlist__card-tag--self' : 'vlist__card-tag--partner'">
              <text>{{ v.isSelfOperated ? '自营' : '合作' }}</text>
            </view>
            <view v-for="surface in v.surfaces.slice(0, 2)" :key="surface" class="vlist__card-tag vlist__card-tag--surface">
              <text>{{ surface }}</text>
            </view>
          </view>
          <!-- Availability overlay -->
          <view class="vlist__card-avail-badge" :class="{ 'vlist__card-avail-badge--empty': !v.hasAvailability }">
            <view class="vlist__card-avail-dot" />
            <text class="vlist__card-avail-text">{{ v.hasAvailability ? '今日有空' : '今日已满' }}</text>
          </view>
        </view>

        <!-- Info -->
        <view class="vlist__card-body">
          <view class="vlist__card-top">
            <text class="vlist__card-name">{{ v.name }}</text>
            <text class="vlist__card-price">¥{{ v.priceFrom }}<text class="vlist__card-price-unit">起</text></text>
          </view>
          <view class="vlist__card-addr-row">
            <cf-icon name="location" :size="18" color="rgba(255,255,255,0.4)" />
            <text class="vlist__card-addr">{{ v.address }}</text>
          </view>
          <view class="vlist__card-bottom">
            <view class="vlist__card-meta-row">
              <text class="vlist__card-meta">{{ v.distanceText }}</text>
              <text class="vlist__card-sep">·</text>
              <text class="vlist__card-meta">{{ v.courtCount }} 块场地</text>
              <text class="vlist__card-sep">·</text>
              <text class="vlist__card-meta">{{ v.hours }}</text>
            </view>
            <view class="vlist__card-book-btn">
              <text class="vlist__card-book-text">预订</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- Loading skeleton -->
    <view v-else class="vlist__list">
      <view v-for="i in 3" :key="i" class="vlist__skeleton">
        <view class="vlist__skeleton-img" />
        <view class="vlist__skeleton-body">
          <view class="vlist__skeleton-line vlist__skeleton-line--lg" />
          <view class="vlist__skeleton-line" />
          <view class="vlist__skeleton-line vlist__skeleton-line--sm" />
        </view>
      </view>
    </view>

    <view style="height: 40rpx;" />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { listVenues } from '@/api/venues'
import CfIcon from '@/components/ui/CfIcon.vue'

const loading = ref(false)
const showSearch = ref(false)
const searchQuery = ref('')
const activeFilter = ref('all')
const sortMode = ref('distance')

const filters = [
  { key: 'all', label: '全部' },
  { key: 'self', label: '自营' },
  { key: 'partner', label: '合作' },
  { key: 'indoor', label: '室内' },
  { key: 'outdoor', label: '室外' },
]

const sortLabel = computed(() => sortMode.value === 'distance' ? '按距离' : '按价格')

// Mock venues data — replace with real API
const venues = ref([
  {
    id: '1', name: '卓越网球中心', address: '朝阳区建国路89号',
    district: '朝阳', distanceText: '1.2km', coverUrl: '/static/venue-placeholder.jpg',
    priceFrom: 80, isSelfOperated: true, hasAvailability: true,
    courtCount: 6, hours: '07:00–22:00',
    surfaces: ['硬地', '红土'],
    isIndoor: true,
  },
  {
    id: '2', name: '国贸户外球场', address: '东城区东长安街1号',
    district: '东城', distanceText: '2.5km', coverUrl: '/static/venue-placeholder.jpg',
    priceFrom: 120, isSelfOperated: false, hasAvailability: true,
    courtCount: 3, hours: '08:00–21:00',
    surfaces: ['硬地'],
    isIndoor: false,
  },
  {
    id: '3', name: '望京体育公园', address: '朝阳区望京街10号',
    district: '朝阳', distanceText: '3.1km', coverUrl: '/static/venue-placeholder.jpg',
    priceFrom: 60, isSelfOperated: true, hasAvailability: false,
    courtCount: 4, hours: '06:00–23:00',
    surfaces: ['红土', '草地'],
    isIndoor: false,
  },
])

const filteredVenues = computed(() => {
  let list = venues.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(v => v.name.includes(q) || v.address.includes(q))
  }
  if (activeFilter.value === 'self') list = list.filter(v => v.isSelfOperated)
  else if (activeFilter.value === 'partner') list = list.filter(v => !v.isSelfOperated)
  else if (activeFilter.value === 'indoor') list = list.filter(v => v.isIndoor)
  else if (activeFilter.value === 'outdoor') list = list.filter(v => !v.isIndoor)
  if (sortMode.value === 'price') list = [...list].sort((a, b) => a.priceFrom - b.priceFrom)
  return list
})

function toggleSearch() {
  showSearch.value = !showSearch.value
  if (!showSearch.value) searchQuery.value = ''
}

function clearSearch() {
  searchQuery.value = ''
  showSearch.value = false
}

function onSearch() {
  // reactive — computed handles it
}

function setFilter(key: string) {
  activeFilter.value = key
}

function toggleSort() {
  sortMode.value = sortMode.value === 'distance' ? 'price' : 'distance'
}

function goDetail(id: string) {
  uni.navigateTo({ url: `/packages/venue/detail/index?id=${id}` })
}
</script>

<style lang="scss">
@import '@/uni.scss';

.vlist {
  background: $cf-bg;
  min-height: 100vh;
}

// ─── Nav ─────────────────────────────────────────────────────────────────────
.vlist__nav {
  background: $cf-bg;
  padding: 0 40rpx;
  border-bottom: 1rpx solid $cf-line;
}

.vlist__nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 88rpx;
}

.vlist__nav-title {
  font-size: 36rpx;
  font-weight: 800;
  color: $cf-white;
  letter-spacing: -0.02em;
}

.vlist__search-btn {
  width: 64rpx;
  height: 64rpx;
  background: $cf-card;
  border-radius: $r-full;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1rpx solid $cf-line;
}

.vlist__search-icon {
  font-size: 28rpx;
}

.vlist__search-bar {
  display: flex;
  align-items: center;
  background: $cf-card;
  border-radius: $r-md;
  margin-bottom: 16rpx;
  padding: 0 24rpx;
  border: 1rpx solid $cf-line-2;
}

.vlist__search-input {
  flex: 1;
  height: 72rpx;
  font-size: 26rpx;
  color: $cf-white;
  background: transparent;
}

.vlist__search-placeholder {
  color: $cf-text-3;
  font-size: 26rpx;
}

.vlist__search-clear {
  font-size: 28rpx;
  color: $cf-text-2;
  padding: 8rpx;
}

// ─── Filters ─────────────────────────────────────────────────────────────────
.vlist__filters-scroll {
  background: $cf-bg;
  border-bottom: 1rpx solid $cf-line;
}

.vlist__filters-row {
  display: flex;
  flex-direction: row;
  padding: 16rpx 32rpx;
  gap: 12rpx;
}

.vlist__filter-chip {
  flex-shrink: 0;
  padding: 10rpx 28rpx;
  border-radius: $r-full;
  background: $cf-card;
  border: 1rpx solid $cf-line;
  &--active {
    background: $cf-accent-dim;
    border-color: rgba(196, 232, 74, 0.35);
  }
}

.vlist__filter-text {
  font-size: 24rpx;
  color: $cf-text-2;
  font-weight: 500;
  .vlist__filter-chip--active & { color: $cf-accent; }
}

// ─── Results header ──────────────────────────────────────────────────────────
.vlist__results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 40rpx;
}

.vlist__results-count {
  font-size: 24rpx;
  color: $cf-text-2;
}

.vlist__sort-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.vlist__sort-text {
  font-size: 24rpx;
  color: $cf-accent;
  font-weight: 500;
}

.vlist__sort-icon {
  font-size: 22rpx;
  color: $cf-accent;
}

// ─── Venue Cards ─────────────────────────────────────────────────────────────
.vlist__list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding: 0 32rpx;
}

.vlist__card {
  background: $cf-card;
  border-radius: $r-xl;
  overflow: hidden;
  border: 1rpx solid $cf-line;
  &:active { opacity: 0.88; }
}

.vlist__card-img-wrap {
  position: relative;
  height: 280rpx;
  background: $cf-card-2;
}

.vlist__card-img {
  width: 100%;
  height: 100%;
}

.vlist__card-img-overlay {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 150rpx;
  background: linear-gradient(to bottom, transparent, rgba(6,13,8,0.85));
}

.vlist__card-tags {
  position: absolute;
  top: 20rpx;
  left: 20rpx;
  display: flex;
  gap: 10rpx;
}

.vlist__card-tag {
  padding: 5rpx 16rpx;
  border-radius: $r-full;
  font-size: 18rpx;
  font-weight: 700;
  &--self { background: $cf-accent; color: #0a1a0d; }
  &--partner { background: $cf-blue-dim; color: $cf-blue; border: 1rpx solid rgba(77,156,239,0.3); }
  &--surface { background: rgba(0,0,0,0.4); color: $cf-white; backdrop-filter: blur(4px); }
}

.vlist__card-avail-badge {
  position: absolute;
  bottom: 20rpx;
  right: 20rpx;
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: rgba(6,13,8,0.7);
  backdrop-filter: blur(4px);
  border-radius: $r-full;
  padding: 8rpx 18rpx;
  border: 1rpx solid rgba(61,204,118,0.3);
  &--empty { border-color: $cf-line; }
}

.vlist__card-avail-dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: $r-full;
  background: $cf-green;
  .vlist__card-avail-badge--empty & { background: $cf-text-3; }
}

.vlist__card-avail-text {
  font-size: 20rpx;
  font-weight: 500;
  color: $cf-green;
  .vlist__card-avail-badge--empty & { color: $cf-text-3; }
}

.vlist__card-body {
  padding: 24rpx 28rpx;
}

.vlist__card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 10rpx;
}

.vlist__card-name {
  font-size: 30rpx;
  font-weight: 700;
  color: $cf-white;
  flex: 1;
  margin-right: 16rpx;
}

.vlist__card-price {
  font-size: 30rpx;
  font-weight: 800;
  color: $cf-accent;
  flex-shrink: 0;
}

.vlist__card-price-unit {
  font-size: 20rpx;
  font-weight: 400;
  color: $cf-text-2;
}

.vlist__card-addr-row {
  display: flex;
  align-items: center;
  gap: 6rpx;
  margin-bottom: 16rpx;
}
.vlist__card-addr {
  font-size: 22rpx;
  color: $cf-text-2;
}

.vlist__card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.vlist__card-meta-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.vlist__card-meta {
  font-size: 20rpx;
  color: $cf-text-3;
}

.vlist__card-sep {
  font-size: 20rpx;
  color: $cf-text-3;
}

.vlist__card-book-btn {
  background: $cf-accent;
  border-radius: $r-full;
  padding: 10rpx 28rpx;
}

.vlist__card-book-text {
  font-size: 22rpx;
  font-weight: 700;
  color: #0a1a0d;
}

// ─── Skeleton ────────────────────────────────────────────────────────────────
.vlist__skeleton {
  background: $cf-card;
  border-radius: $r-xl;
  overflow: hidden;
  border: 1rpx solid $cf-line;
}

.vlist__skeleton-img {
  height: 280rpx;
  background: $cf-card-2;
  animation: shimmer 1.5s infinite;
}

.vlist__skeleton-body {
  padding: 24rpx 28rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.vlist__skeleton-line {
  height: 24rpx;
  background: $cf-card-2;
  border-radius: $r-sm;
  animation: shimmer 1.5s infinite;
  width: 70%;
  &--lg { width: 90%; height: 32rpx; }
  &--sm { width: 50%; }
}

@keyframes shimmer {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}
</style>
