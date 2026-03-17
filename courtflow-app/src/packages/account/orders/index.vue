<template>
  <view class="orders">
    <view class="orders__nav">
      <view class="orders__back" @tap="goBack">
        <cf-icon name="chevron-left" :size="22" color="rgba(255,255,255,0.85)" />
      </view>
      <text class="orders__nav-title">我的订单</text>
      <view style="width: 64rpx;" />
    </view>

    <!-- Tab bar -->
    <view class="orders__tabs">
      <view
        v-for="tab in tabs"
        :key="tab.key"
        class="orders__tab"
        :class="{ 'orders__tab--active': activeTab === tab.key }"
        @tap="setTab(tab.key)"
      >
        <text class="orders__tab-text">{{ tab.label }}</text>
        <view v-if="activeTab === tab.key" class="orders__tab-indicator" />
      </view>
    </view>

    <!-- Order list -->
    <scroll-view class="orders__scroll" scroll-y @scrolltolower="loadMore">
      <view v-if="filteredOrders.length > 0" class="orders__list">
        <view
          v-for="order in filteredOrders"
          :key="order.id"
          class="orders__card"
          @tap="goOrderDetail(order.id)"
        >
          <!-- Card header -->
          <view class="orders__card-header">
            <view class="orders__card-venue-row">
              <text class="orders__card-venue">{{ order.venueName }}</text>
              <view class="orders__card-status-badge" :class="`orders__card-status-badge--${order.status}`">
                <text class="orders__card-status-text">{{ order.statusText }}</text>
              </view>
            </view>
            <text class="orders__card-no">订单号 {{ order.orderNo }}</text>
          </view>

          <view class="orders__card-divider" />

          <!-- Court + time items -->
          <view v-for="(slot, i) in order.slots.slice(0, 2)" :key="i" class="orders__card-slot">
            <view class="orders__card-slot-icon-wrap">
              <cf-icon name="court" :size="18" color="#B8D430" />
            </view>
            <view class="orders__card-slot-info">
              <text class="orders__card-slot-court">{{ slot.courtName }}</text>
              <text class="orders__card-slot-time">{{ slot.date }} · {{ slot.timeRange }}</text>
            </view>
          </view>
          <view v-if="order.slots.length > 2" class="orders__card-more">
            <text class="orders__card-more-text">+{{ order.slots.length - 2 }} 个时段</text>
          </view>

          <view class="orders__card-divider" />

          <!-- Footer row -->
          <view class="orders__card-footer">
            <view class="orders__card-footer-left">
              <text class="orders__card-slots-count">{{ order.slots.length }} 个时段</text>
              <text class="orders__card-total">¥{{ order.total }}</text>
            </view>
            <view class="orders__card-action-btn" :class="`orders__card-action-btn--${order.status}`" @tap.stop="onAction(order)">
              <text class="orders__card-action-text">{{ order.actionText }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Empty state -->
      <view v-else class="orders__empty">
        <cf-icon name="document" :size="64" color="rgba(255,255,255,0.15)" />
        <text class="orders__empty-text">暂无{{ tabLabel }}订单</text>
        <view class="orders__empty-btn" @tap="goBook">
          <text class="orders__empty-btn-text">去预订场地</text>
        </view>
      </view>

      <view style="height: 60rpx;" />
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'

const activeTab = ref('all')

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'pending', label: '待支付' },
  { key: 'confirmed', label: '已完成' },
  { key: 'cancelled', label: '已取消' },
]

const tabLabel = computed(() => tabs.find(t => t.key === activeTab.value)?.label ?? '')

// Mock data
const allOrders = ref([
  {
    id: '1', orderNo: 'CF20240001', venueName: '卓越网球中心',
    status: 'confirmed', statusText: '已完成',
    total: '240', actionText: '再次预订',
    slots: [
      { courtName: '1号场 (硬地)', date: '03月15日', timeRange: '10:00–11:00' },
      { courtName: '2号场 (硬地)', date: '03月15日', timeRange: '10:00–11:00' },
    ],
  },
  {
    id: '2', orderNo: 'CF20240002', venueName: '国贸球场',
    status: 'pending', statusText: '待支付',
    total: '120', actionText: '去支付',
    slots: [
      { courtName: '1号场 (硬地)', date: '03月22日', timeRange: '14:00–15:00' },
    ],
  },
  {
    id: '3', orderNo: 'CF20240003', venueName: '望京体育公园',
    status: 'cancelled', statusText: '已取消',
    total: '180', actionText: '查看详情',
    slots: [
      { courtName: '3号场 (红土)', date: '03月10日', timeRange: '09:00–10:00' },
    ],
  },
])

const filteredOrders = computed(() => {
  if (activeTab.value === 'all') return allOrders.value
  return allOrders.value.filter(o => o.status === activeTab.value)
})

function setTab(key: string) {
  activeTab.value = key
}

function goOrderDetail(id: string) {
  uni.navigateTo({ url: `/packages/booking/result/index?orderId=${id}&success=1` })
}

function onAction(order: any) {
  if (order.status === 'pending') {
    uni.navigateTo({ url: `/packages/booking/order/index?orderId=${order.id}` })
  } else {
    goOrderDetail(order.id)
  }
}

function goBook() {
  uni.navigateTo({ url: '/packages/venue/list/index' })
}

function goBack() {
  uni.navigateBack()
}

function loadMore() {
  // Pagination — Phase 2
}
</script>

<style lang="scss">
@import '@/uni.scss';

.orders {
  background: $cf-bg;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

// ─── Nav ─────────────────────────────────────────────────────────────────────
.orders__nav {
  display: flex;
  align-items: center;
  padding: 0 24rpx;
  height: 88rpx;
  background: $cf-surface;
  border-bottom: 1rpx solid $cf-line;
}

.orders__back {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $cf-card;
  border-radius: $r-full;
  border: 1rpx solid $cf-line;
}

.orders__back-icon {
  font-size: 44rpx;
  color: $cf-white;
  font-weight: 300;
}

.orders__nav-title {
  flex: 1;
  text-align: center;
  font-size: 30rpx;
  font-weight: 700;
  color: $cf-white;
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────
.orders__tabs {
  display: flex;
  flex-direction: row;
  background: $cf-surface;
  border-bottom: 1rpx solid $cf-line;
}

.orders__tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0 16rpx;
  position: relative;
}

.orders__tab-text {
  font-size: 26rpx;
  color: $cf-text-2;
  font-weight: 500;
  .orders__tab--active & { color: $cf-accent; font-weight: 700; }
}

.orders__tab-indicator {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40rpx;
  height: 4rpx;
  background: $cf-accent;
  border-radius: $r-full;
}

// ─── List ─────────────────────────────────────────────────────────────────────
.orders__scroll {
  flex: 1;
}

.orders__list {
  padding: 20rpx 32rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

// ─── Order card ──────────────────────────────────────────────────────────────
.orders__card {
  background: $cf-card;
  border-radius: $r-xl;
  border: 1rpx solid $cf-line;
  overflow: hidden;
  &:active { opacity: 0.9; }
}

.orders__card-header {
  padding: 20rpx 24rpx 16rpx;
}

.orders__card-venue-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8rpx;
}

.orders__card-venue {
  font-size: 28rpx;
  font-weight: 700;
  color: $cf-white;
}

.orders__card-status-badge {
  padding: 5rpx 16rpx;
  border-radius: $r-full;
  font-size: 18rpx;
  &--confirmed { background: rgba(61,204,118,0.12); border: 1rpx solid rgba(61,204,118,0.3); }
  &--pending { background: $cf-amber-dim; border: 1rpx solid rgba(245,166,35,0.3); }
  &--cancelled { background: rgba(255,255,255,0.05); border: 1rpx solid $cf-line; }
}

.orders__card-status-text {
  font-size: 18rpx;
  font-weight: 600;
  .orders__card-status-badge--confirmed & { color: $cf-green; }
  .orders__card-status-badge--pending & { color: $cf-amber; }
  .orders__card-status-badge--cancelled & { color: $cf-text-3; }
}

.orders__card-no {
  font-size: 20rpx;
  color: $cf-text-3;
  font-family: 'Courier New', monospace;
}

.orders__card-divider {
  height: 1rpx;
  background: $cf-line;
}

// Slot rows
.orders__card-slot {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 24rpx;
  border-bottom: 1rpx solid $cf-line;
  &:last-of-type { border-bottom: none; }
}

.orders__card-slot-icon-wrap {
  width: 48rpx;
  height: 48rpx;
  background: $cf-card-2;
  border-radius: $r-sm;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.orders__card-slot-icon {
  font-size: 24rpx;
}

.orders__card-slot-court {
  font-size: 24rpx;
  font-weight: 600;
  color: $cf-white;
  display: block;
}

.orders__card-slot-time {
  font-size: 20rpx;
  color: $cf-text-2;
  margin-top: 4rpx;
  display: block;
}

.orders__card-more {
  padding: 10rpx 24rpx;
  border-bottom: 1rpx solid $cf-line;
}

.orders__card-more-text {
  font-size: 20rpx;
  color: $cf-text-2;
}

// Footer
.orders__card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 24rpx;
}

.orders__card-footer-left {
  display: flex;
  align-items: baseline;
  gap: 12rpx;
}

.orders__card-slots-count {
  font-size: 22rpx;
  color: $cf-text-2;
}

.orders__card-total {
  font-size: 32rpx;
  font-weight: 900;
  color: $cf-accent;
}

.orders__card-action-btn {
  padding: 10rpx 28rpx;
  border-radius: $r-full;
  &--confirmed { background: $cf-card-2; border: 1rpx solid $cf-line; }
  &--pending { background: $cf-accent; }
  &--cancelled { background: $cf-card-2; border: 1rpx solid $cf-line; }
}

.orders__card-action-text {
  font-size: 22rpx;
  font-weight: 600;
  .orders__card-action-btn--confirmed & { color: $cf-text-2; }
  .orders__card-action-btn--pending & { color: #0a1a0d; }
  .orders__card-action-btn--cancelled & { color: $cf-text-2; }
}

// ─── Empty ────────────────────────────────────────────────────────────────────
.orders__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 48rpx;
  gap: 20rpx;
}

.orders__empty-icon {
  font-size: 80rpx;
}

.orders__empty-text {
  font-size: 28rpx;
  color: $cf-text-2;
}

.orders__empty-btn {
  background: $cf-accent;
  border-radius: $r-full;
  padding: 16rpx 56rpx;
  margin-top: 8rpx;
  &:active { opacity: 0.85; }
}

.orders__empty-btn-text {
  font-size: 26rpx;
  font-weight: 700;
  color: #0a1a0d;
}
</style>
