<template>
  <view class="result">
    <!-- Background -->
    <view class="result__bg">
      <view class="result__bg-ring result__bg-ring--1" />
      <view class="result__bg-ring result__bg-ring--2" />
      <view class="result__bg-ring result__bg-ring--3" />
    </view>

    <view class="result__content">
      <!-- Status icon -->
      <view class="result__icon-wrap" :class="success ? 'result__icon-wrap--success' : 'result__icon-wrap--fail'">
        <view class="result__icon-ring" />
        <cf-icon :name="success ? 'check' : 'close'" :size="36" :color="success ? '#34d399' : '#F04545'" />
      </view>

      <!-- Title & subtitle -->
      <text class="result__title">{{ success ? '支付成功' : '支付失败' }}</text>
      <text class="result__subtitle">
        {{ success ? '您的球场已预订成功，请准时到场' : '支付遇到问题，请重新尝试' }}
      </text>

      <!-- Order summary card -->
      <view v-if="success" class="result__card">
        <view class="result__card-header">
          <text class="result__card-header-text">订单信息</text>
          <text class="result__order-no">NO. {{ orderNo }}</text>
        </view>
        <view class="result__card-divider" />
        <view v-for="(item, i) in orderItems" :key="i" class="result__card-item">
          <view class="result__card-item-icon-wrap">
            <cf-icon name="court" :size="20" color="#B8D430" />
          </view>
          <view class="result__card-item-info">
            <text class="result__card-item-venue">{{ item.venueName }}</text>
            <text class="result__card-item-detail">{{ item.courtName }} · {{ item.date }} {{ item.timeRange }}</text>
          </view>
        </view>
        <view class="result__card-divider" />
        <view class="result__card-total-row">
          <text class="result__card-total-label">实付金额</text>
          <text class="result__card-total-value">¥{{ totalPaid }}</text>
        </view>
      </view>

      <!-- Tip -->
      <view v-if="success" class="result__tip">
        <cf-icon name="bell" :size="18" color="#FBBF24" />
        <text class="result__tip-text">请携带本订单号前往场馆，如需帮助请联系客服</text>
      </view>
    </view>

    <!-- Actions -->
    <view class="result__actions">
      <view v-if="success" class="result__btn result__btn--primary" @tap="goOrders">
        <text class="result__btn-text">查看订单</text>
      </view>
      <view v-else class="result__btn result__btn--primary" @tap="goBack">
        <text class="result__btn-text">重新支付</text>
      </view>
      <view class="result__btn result__btn--outline" @tap="goHome">
        <text class="result__btn-text result__btn-text--outline">返回首页</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'

const pages = getCurrentPages()
const currentPage = pages[pages.length - 1] as any
const success = ref(currentPage.options?.success === '1')
const orderNo = ref('CF' + Date.now().toString().slice(-8))

const orderItems = ref([
  {
    venueName: '卓越网球中心',
    courtName: '1号场',
    date: '03月20日',
    timeRange: '10:00–11:00',
  },
  {
    venueName: '卓越网球中心',
    courtName: '2号场',
    date: '03月20日',
    timeRange: '10:00–11:00',
  },
])

const totalPaid = ref('240')

function goOrders() {
  uni.reLaunch({ url: '/packages/account/orders/index' })
}

function goBack() {
  uni.navigateBack({ delta: 2 })
}

function goHome() {
  uni.switchTab({ url: '/pages/index/index' })
}
</script>

<style lang="scss">
@import '@/uni.scss';

.result {
  min-height: 100vh;
  background: $cf-bg;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

// ─── Background rings ────────────────────────────────────────────────────────
.result__bg {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 600rpx;
  pointer-events: none;
}

.result__bg-ring {
  position: absolute;
  border-radius: $r-full;
  border: 1rpx solid rgba(196,232,74,0.07);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.result__bg-ring--1 { width: 320rpx; height: 320rpx; }
.result__bg-ring--2 { width: 520rpx; height: 520rpx; opacity: 0.6; }
.result__bg-ring--3 { width: 720rpx; height: 720rpx; opacity: 0.3; }

// ─── Content ─────────────────────────────────────────────────────────────────
.result__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 48rpx 48rpx;
}

.result__icon-wrap {
  width: 160rpx;
  height: 160rpx;
  border-radius: $r-full;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: 40rpx;
  &--success {
    background: rgba(61,204,118,0.12);
    border: 3rpx solid rgba(61,204,118,0.4);
  }
  &--fail {
    background: rgba(232,85,85,0.1);
    border: 3rpx solid rgba(232,85,85,0.3);
  }
}

.result__icon-ring {
  position: absolute;
  inset: -16rpx;
  border-radius: $r-full;
  border: 1rpx solid rgba(61,204,118,0.15);
  .result__icon-wrap--fail & { border-color: rgba(232,85,85,0.1); }
}

.result__icon {
  font-size: 72rpx;
  font-weight: 900;
  color: $cf-green;
  .result__icon-wrap--fail & { color: $cf-red; }
}

.result__title {
  font-size: 56rpx;
  font-weight: 900;
  color: $cf-white;
  letter-spacing: -0.03em;
  display: block;
  margin-bottom: 16rpx;
  text-align: center;
}

.result__subtitle {
  font-size: 26rpx;
  color: $cf-text-2;
  display: block;
  text-align: center;
  margin-bottom: 48rpx;
}

// ─── Card ─────────────────────────────────────────────────────────────────────
.result__card {
  width: 100%;
  background: $cf-card;
  border-radius: $r-xl;
  border: 1rpx solid $cf-line;
  overflow: hidden;
  margin-bottom: 24rpx;
}

.result__card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 28rpx;
}

.result__card-header-text {
  font-size: 24rpx;
  font-weight: 700;
  color: $cf-text-2;
  letter-spacing: 0.06em;
}

.result__order-no {
  font-size: 20rpx;
  color: $cf-text-3;
  font-family: 'Courier New', monospace;
}

.result__card-divider {
  height: 1rpx;
  background: $cf-line;
}

.result__card-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 20rpx 28rpx;
  border-bottom: 1rpx solid $cf-line;
  &:last-of-type { border-bottom: none; }
}

.result__card-item-icon-wrap {
  width: 56rpx;
  height: 56rpx;
  background: $cf-accent-dim;
  border-radius: $r-md;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.result__card-item-icon {
  font-size: 28rpx;
}

.result__card-item-info {
  flex: 1;
}

.result__card-item-venue {
  font-size: 26rpx;
  font-weight: 600;
  color: $cf-white;
  display: block;
}

.result__card-item-detail {
  font-size: 22rpx;
  color: $cf-text-2;
  margin-top: 4rpx;
  display: block;
}

.result__card-total-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 28rpx;
}

.result__card-total-label {
  font-size: 26rpx;
  color: $cf-text-2;
  font-weight: 500;
}

.result__card-total-value {
  font-size: 40rpx;
  font-weight: 900;
  color: $cf-accent;
}

// ─── Tip ─────────────────────────────────────────────────────────────────────
.result__tip {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  background: $cf-card;
  border-radius: $r-md;
  padding: 20rpx 24rpx;
  border: 1rpx solid $cf-line;
  width: 100%;
}

.result__tip-icon {
  font-size: 24rpx;
  flex-shrink: 0;
  margin-top: 2rpx;
}

.result__tip-text {
  font-size: 22rpx;
  color: $cf-text-2;
  line-height: 1.6;
}

// ─── Actions ─────────────────────────────────────────────────────────────────
.result__actions {
  padding: 32rpx 48rpx;
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.result__btn {
  width: 100%;
  height: 96rpx;
  border-radius: $r-full;
  display: flex;
  align-items: center;
  justify-content: center;
  &--primary { background: $cf-accent; &:active { opacity: 0.85; } }
  &--outline { background: transparent; border: 1.5rpx solid $cf-line-2; &:active { background: $cf-card; } }
}

.result__btn-text {
  font-size: 30rpx;
  font-weight: 700;
  color: #0a1a0d;
  &--outline { color: $cf-text-2; font-weight: 500; }
}
</style>
