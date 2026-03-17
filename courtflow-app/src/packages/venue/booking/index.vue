<template>
  <view class="vbooking">
    <!-- Venue header bar -->
    <view class="vbooking__header">
      <view class="vbooking__back" @tap="goBack">
        <cf-icon name="chevron-left" :size="22" color="rgba(255,255,255,0.85)" />
      </view>
      <view class="vbooking__header-center">
        <text class="vbooking__header-name">{{ venueName }}</text>
        <text class="vbooking__header-sub">选择日期与时段</text>
      </view>
      <view class="vbooking__header-right" />
    </view>

    <!-- Date tabs -->
    <scroll-view class="vbooking__date-scroll" scroll-x :scroll-into-view="`date-${selectedDate}`">
      <view class="vbooking__date-row">
        <view
          v-for="d in dateTabs"
          :key="d.dateStr"
          :id="`date-${d.dateStr}`"
          class="vbooking__date-tab"
          :class="{ 'vbooking__date-tab--active': d.dateStr === selectedDate }"
          @tap="onSelectDate(d.dateStr)"
        >
          <text class="vbooking__date-wd">{{ d.weekday }}</text>
          <text class="vbooking__date-day">{{ d.day }}</text>
          <view v-if="d.isToday" class="vbooking__date-today-dot" />
        </view>
      </view>
    </scroll-view>

    <!-- Legend -->
    <view class="vbooking__legend">
      <view v-for="l in legend" :key="l.key" class="vbooking__legend-item">
        <view class="vbooking__legend-dot" :class="`vbooking__legend-dot--${l.key}`" />
        <text class="vbooking__legend-label">{{ l.label }}</text>
      </view>
    </view>

    <!-- Booking grid -->
    <scroll-view class="vbooking__grid-wrap" scroll-y>
      <BookingGrid
        v-if="grid"
        :grid="grid"
        :courts="courts"
        :selected-date="selectedDate"
        :date-tabs="dateTabs"
        :slot-duration-minutes="60"
        open-time="07:00"
        close-time="22:00"
        :selected-slot-keys="bookingStore.selectedSlotKeys"
        :loading="loadingGrid"
        @select-date="onSelectDate"
        @toggle-slot="onToggleSlot"
      />
      <view v-else-if="loadingGrid" class="vbooking__loading">
        <view class="vbooking__loading-spinner" />
        <text class="vbooking__loading-text">加载中…</text>
      </view>
      <view style="height: 240rpx;" />
    </scroll-view>

    <!-- Selection panel (slides up when slots selected) -->
    <view class="vbooking__panel" :class="{ 'vbooking__panel--visible': bookingStore.selectedCount > 0 }">
      <view class="vbooking__panel-inner">
        <view class="vbooking__panel-info">
          <text class="vbooking__panel-count">已选 {{ bookingStore.selectedCount }} 个时段</text>
          <text class="vbooking__panel-total">¥{{ totalYuan }}</text>
        </view>
        <view class="vbooking__panel-btn" @tap="goOrder">
          <text class="vbooking__panel-btn-text">去下单</text>
          <cf-icon name="chevron-right" :size="18" color="#fff" />
        </view>
      </view>
      <view class="vbooking__panel-hint" v-if="bookingStore.activeHolds.length > 0">
        <view class="vbooking__panel-hold-dot" />
        <text class="vbooking__panel-hint-text">时段已锁定，请在 5 分钟内完成支付</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import BookingGrid from '@/components/domain/BookingGrid/index.vue'
import { useBookingStore } from '@/stores/booking'
import CfIcon from '@/components/ui/CfIcon.vue'
import type { SlotInfo } from '@/types'

const bookingStore = useBookingStore()
const loadingGrid = ref(false)

// Route params
const pages = getCurrentPages()
const currentPage = pages[pages.length - 1] as any
const venueId = ref(currentPage.options?.venueId ?? '1')
const venueName = ref(decodeURIComponent(currentPage.options?.venueName ?? '门店预订'))

const legend = [
  { key: 'available', label: '可预订' },
  { key: 'selected', label: '已选中' },
  { key: 'held', label: '锁定中' },
  { key: 'unavailable', label: '不可订' },
]

// Date tabs — next 7 days
const dateTabs = computed(() => {
  const days = []
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  for (let i = 0; i < 7; i++) {
    const d = new Date()
    d.setDate(d.getDate() + i)
    const pad = (n: number) => String(n).padStart(2, '0')
    const dateStr = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
    days.push({
      dateStr,
      weekday: i === 0 ? '今' : `周${weekdays[d.getDay()]}`,
      day: d.getDate(),
      isToday: i === 0,
    })
  }
  return days
})

const selectedDate = computed(() => bookingStore.currentDate || dateTabs.value[0]?.dateStr || '')

const grid = computed(() => bookingStore.grid)

const courts = ref([
  { id: 'c1', name: '1号场', typeName: '硬地' },
  { id: 'c2', name: '2号场', typeName: '硬地' },
  { id: 'c3', name: '3号场', typeName: '红土' },
  { id: 'c4', name: '4号场', typeName: '红土' },
])

const totalYuan = computed(() => (bookingStore.totalCents / 100).toFixed(0))

onMounted(async () => {
  bookingStore.venueId = venueId.value
  if (!bookingStore.currentDate) {
    bookingStore.currentDate = dateTabs.value[0]?.dateStr ?? ''
  }
  await loadGrid()
})

async function loadGrid() {
  loadingGrid.value = true
  try {
    await bookingStore.loadGrid(venueId.value, selectedDate.value)
  } finally {
    loadingGrid.value = false
  }
}

async function onSelectDate(date: string) {
  bookingStore.currentDate = date
  await loadGrid()
}

function onToggleSlot(slot: SlotInfo) {
  bookingStore.toggleSlot(slot)
}

async function goOrder() {
  if (bookingStore.selectedCount === 0) return
  // Submit hold first
  try {
    await bookingStore.submitHold(venueId.value, '')
    uni.navigateTo({ url: '/packages/booking/order/index' })
  } catch (e) {
    uni.showToast({ title: '锁定失败，请重试', icon: 'none' })
  }
}

function goBack() {
  uni.navigateBack()
}
</script>

<style lang="scss">
@import '@/uni.scss';

.vbooking {
  background: $cf-bg;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

// ─── Header ──────────────────────────────────────────────────────────────────
.vbooking__header {
  display: flex;
  align-items: center;
  padding: 0 24rpx;
  height: 88rpx;
  background: $cf-surface;
  border-bottom: 1rpx solid $cf-line;
}

.vbooking__back {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: $r-full;
  background: $cf-card;
  border: 1rpx solid $cf-line;
}

.vbooking__back-icon {
  font-size: 44rpx;
  color: $cf-white;
  font-weight: 300;
}

.vbooking__header-center {
  flex: 1;
  text-align: center;
}

.vbooking__header-name {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $cf-white;
}

.vbooking__header-sub {
  display: block;
  font-size: 20rpx;
  color: $cf-text-2;
  margin-top: 2rpx;
}

.vbooking__header-right {
  width: 64rpx;
}

// ─── Date tabs ───────────────────────────────────────────────────────────────
.vbooking__date-scroll {
  background: $cf-surface;
  border-bottom: 1rpx solid $cf-line;
  flex-shrink: 0;
}

.vbooking__date-row {
  display: flex;
  flex-direction: row;
  padding: 12rpx 24rpx;
  gap: 12rpx;
}

.vbooking__date-tab {
  flex-shrink: 0;
  min-width: 88rpx;
  padding: 14rpx 16rpx;
  border-radius: $r-md;
  background: $cf-card;
  border: 1rpx solid $cf-line;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  &--active {
    background: $cf-accent-dim;
    border-color: rgba(196,232,74,0.4);
  }
}

.vbooking__date-wd {
  font-size: 18rpx;
  color: $cf-text-2;
  .vbooking__date-tab--active & { color: $cf-accent; }
}

.vbooking__date-day {
  font-size: 32rpx;
  font-weight: 800;
  color: $cf-white;
  line-height: 1;
}

.vbooking__date-today-dot {
  width: 8rpx;
  height: 8rpx;
  background: $cf-accent;
  border-radius: $r-full;
  margin-top: 2rpx;
}

// ─── Legend ──────────────────────────────────────────────────────────────────
.vbooking__legend {
  display: flex;
  flex-direction: row;
  gap: 24rpx;
  padding: 14rpx 32rpx;
  background: $cf-surface;
  border-bottom: 1rpx solid $cf-line;
  flex-shrink: 0;
}

.vbooking__legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.vbooking__legend-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 4rpx;
  &--available { background: $cf-card-2; border: 1rpx solid $cf-line-2; }
  &--selected { background: $cf-accent; }
  &--held { background: $cf-amber; }
  &--unavailable { background: $cf-text-3; opacity: 0.5; }
}

.vbooking__legend-label {
  font-size: 20rpx;
  color: $cf-text-2;
}

// ─── Grid wrap ───────────────────────────────────────────────────────────────
.vbooking__grid-wrap {
  flex: 1;
}

.vbooking__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 40rpx;
  gap: 24rpx;
}

.vbooking__loading-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid $cf-card-2;
  border-top-color: $cf-accent;
  border-radius: $r-full;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.vbooking__loading-text {
  font-size: 26rpx;
  color: $cf-text-2;
}

// ─── Selection panel ─────────────────────────────────────────────────────────
.vbooking__panel {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: $cf-surface;
  border-top: 1rpx solid $cf-line-2;
  transform: translateY(100%);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  padding-bottom: env(safe-area-inset-bottom);
  &--visible { transform: translateY(0); }
}

.vbooking__panel-inner {
  display: flex;
  align-items: center;
  padding: 20rpx 32rpx 16rpx;
  gap: 20rpx;
}

.vbooking__panel-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.vbooking__panel-count {
  font-size: 22rpx;
  color: $cf-text-2;
}

.vbooking__panel-total {
  font-size: 44rpx;
  font-weight: 900;
  color: $cf-accent;
  letter-spacing: -0.02em;
}

.vbooking__panel-btn {
  background: $cf-accent;
  border-radius: $r-full;
  padding: 0 40rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  &:active { opacity: 0.85; }
}

.vbooking__panel-btn-text {
  font-size: 28rpx;
  font-weight: 700;
  color: #0a1a0d;
}

.vbooking__panel-btn-arrow {
  font-size: 28rpx;
  font-weight: 700;
  color: #0a1a0d;
}

.vbooking__panel-hint {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 0 32rpx 16rpx;
}

.vbooking__panel-hold-dot {
  width: 10rpx;
  height: 10rpx;
  background: $cf-amber;
  border-radius: $r-full;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.8); }
}

.vbooking__panel-hint-text {
  font-size: 20rpx;
  color: $cf-amber;
}
</style>
