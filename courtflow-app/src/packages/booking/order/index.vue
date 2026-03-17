<template>
  <view class="order">
    <view class="order__nav">
      <view class="order__back" @tap="goBack">
        <cf-icon name="chevron-left" :size="22" color="rgba(255,255,255,0.85)" />
      </view>
      <text class="order__nav-title">确认订单</text>
      <view style="width: 64rpx;" />
    </view>

    <scroll-view class="order__scroll" scroll-y>
      <!-- Hold timer -->
      <view v-if="holdTimeLeft > 0" class="order__timer">
        <view class="order__timer-dot" />
        <text class="order__timer-text">时段锁定中，请在 </text>
        <text class="order__timer-count">{{ holdTimeLeft }}秒</text>
        <text class="order__timer-text"> 内完成支付</text>
      </view>

      <!-- Order items -->
      <view class="order__section">
        <text class="order__section-title">预订详情</text>
        <view
          v-for="(item, i) in orderItems"
          :key="i"
          class="order__item"
        >
          <view class="order__item-left">
            <view class="order__item-index">
              <text class="order__item-index-text">{{ i + 1 }}</text>
            </view>
          </view>
          <view class="order__item-right">
            <text class="order__item-venue">{{ item.venueName }}</text>
            <text class="order__item-court">{{ item.courtName }}</text>
            <view class="order__item-time-row">
              <text class="order__item-date">{{ item.date }}</text>
              <text class="order__item-sep">·</text>
              <text class="order__item-time">{{ item.startTime }} – {{ item.endTime }}</text>
            </view>
          </view>
          <text class="order__item-price">¥{{ item.price }}</text>
        </view>
      </view>

      <!-- Contact -->
      <view class="order__section">
        <text class="order__section-title">联系方式</text>
        <view class="order__contact-row">
          <view class="order__contact-icon-wrap">
            <cf-icon name="phone" :size="20" color="#2E86C1" />
          </view>
          <view class="order__contact-content">
            <text class="order__contact-label">联系电话</text>
            <input
              v-model="contactPhone"
              class="order__phone-input"
              type="number"
              placeholder="请输入手机号"
              placeholder-class="order__phone-placeholder"
              maxlength="11"
            />
          </view>
          <text v-if="contactPhone" class="order__contact-clear" @tap="contactPhone = ''">✕</text>
        </view>
      </view>

      <!-- Coupon -->
      <view class="order__section">
        <view class="order__coupon-row" @tap="showCouponPicker">
          <view class="order__coupon-left">
            <cf-icon name="ticket" :size="20" color="#FBBF24" />
            <text class="order__coupon-label">优惠券</text>
          </view>
          <view class="order__coupon-right">
            <text class="order__coupon-value" :class="{ 'order__coupon-value--active': selectedCoupon }">
              {{ selectedCoupon ? `-¥${selectedCoupon.discount}` : '暂无可用' }}
            </text>
            <text class="order__coupon-arrow">›</text>
          </view>
        </view>
      </view>

      <!-- Price breakdown -->
      <view class="order__section">
        <text class="order__section-title">费用明细</text>
        <view class="order__price-rows">
          <view class="order__price-row">
            <text class="order__price-label">场地费用</text>
            <text class="order__price-value">¥{{ courtFee }}</text>
          </view>
          <view v-if="selectedCoupon" class="order__price-row order__price-row--discount">
            <text class="order__price-label">优惠券抵扣</text>
            <text class="order__price-value order__price-value--discount">-¥{{ selectedCoupon.discount }}</text>
          </view>
          <view class="order__price-divider" />
          <view class="order__price-row order__price-row--total">
            <text class="order__price-label order__price-label--total">实付金额</text>
            <text class="order__price-value order__price-value--total">¥{{ totalFee }}</text>
          </view>
        </view>
      </view>

      <view style="height: 200rpx;" />
    </scroll-view>

    <!-- Pay footer -->
    <view class="order__footer">
      <view class="order__footer-inner">
        <view class="order__footer-price-wrap">
          <text class="order__footer-label">实付</text>
          <text class="order__footer-total">¥{{ totalFee }}</text>
        </view>
        <view class="order__pay-btn" :class="{ 'order__pay-btn--disabled': paying }" @tap="submitOrder">
          <text v-if="!paying" class="order__pay-btn-text">微信支付</text>
          <text v-else class="order__pay-btn-text">处理中…</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useBookingStore } from '@/stores/booking'
import CfIcon from '@/components/ui/CfIcon.vue'

const bookingStore = useBookingStore()

const contactPhone = ref('')
const paying = ref(false)
const holdTimeLeft = ref(300)
const selectedCoupon = ref<{ discount: number } | null>(null)

let timer: any = null

// Mock order items from store — replace with real data
const orderItems = ref([
  {
    venueName: '卓越网球中心',
    courtName: '1号场 (硬地)',
    date: '03月20日 周四',
    startTime: '10:00',
    endTime: '11:00',
    price: '120',
  },
  {
    venueName: '卓越网球中心',
    courtName: '2号场 (硬地)',
    date: '03月20日 周四',
    startTime: '10:00',
    endTime: '11:00',
    price: '120',
  },
])

const courtFee = computed(() =>
  orderItems.value.reduce((sum, item) => sum + parseInt(item.price), 0)
)

const totalFee = computed(() =>
  courtFee.value - (selectedCoupon.value?.discount ?? 0)
)

onMounted(() => {
  timer = setInterval(() => {
    if (holdTimeLeft.value > 0) holdTimeLeft.value--
    else clearInterval(timer)
  }, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
})

async function submitOrder() {
  if (paying.value) return
  if (!contactPhone.value || contactPhone.value.length < 11) {
    uni.showToast({ title: '请填写正确的手机号', icon: 'none' })
    return
  }
  paying.value = true
  try {
    // TODO: create order + trigger WeChat Pay
    await new Promise(r => setTimeout(r, 1200)) // mock delay
    uni.redirectTo({ url: '/packages/booking/result/index?success=1' })
  } catch {
    paying.value = false
    uni.showToast({ title: '支付失败，请重试', icon: 'none' })
  }
}

function goBack() {
  uni.navigateBack()
}

function showCouponPicker() {
  uni.showToast({ title: '暂无可用优惠券', icon: 'none' })
}
</script>

<style lang="scss">
@import '@/uni.scss';

.order {
  background: $cf-bg;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

// ─── Nav ─────────────────────────────────────────────────────────────────────
.order__nav {
  display: flex;
  align-items: center;
  padding: 0 24rpx;
  height: 88rpx;
  background: $cf-surface;
  border-bottom: 1rpx solid $cf-line;
}

.order__back {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $cf-card;
  border-radius: $r-full;
  border: 1rpx solid $cf-line;
}

.order__back-icon {
  font-size: 44rpx;
  color: $cf-white;
  font-weight: 300;
}

.order__nav-title {
  flex: 1;
  text-align: center;
  font-size: 30rpx;
  font-weight: 700;
  color: $cf-white;
}

// ─── Timer ───────────────────────────────────────────────────────────────────
.order__timer {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: $cf-amber-dim;
  border-bottom: 1rpx solid rgba(245,166,35,0.2);
  padding: 16rpx 32rpx;
}

.order__timer-dot {
  width: 12rpx;
  height: 12rpx;
  background: $cf-amber;
  border-radius: $r-full;
  animation: pulse 1.5s ease-in-out infinite;
  flex-shrink: 0;
}

.order__timer-text {
  font-size: 22rpx;
  color: $cf-amber;
}

.order__timer-count {
  font-size: 26rpx;
  font-weight: 800;
  color: $cf-amber;
}

// ─── Scroll ───────────────────────────────────────────────────────────────────
.order__scroll {
  flex: 1;
}

// ─── Section ─────────────────────────────────────────────────────────────────
.order__section {
  margin: 16rpx 32rpx 0;
  background: $cf-card;
  border-radius: $r-xl;
  padding: 24rpx 28rpx;
  border: 1rpx solid $cf-line;
}

.order__section-title {
  font-size: 22rpx;
  font-weight: 700;
  color: $cf-text-2;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  display: block;
  margin-bottom: 20rpx;
}

// ─── Order items ─────────────────────────────────────────────────────────────
.order__item {
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
  padding: 16rpx 0;
  border-bottom: 1rpx solid $cf-line;
  &:last-child { border-bottom: none; padding-bottom: 0; }
  &:first-child { padding-top: 0; }
}

.order__item-left {}

.order__item-index {
  width: 40rpx;
  height: 40rpx;
  border-radius: $r-full;
  background: $cf-accent-dim;
  border: 1rpx solid rgba(196,232,74,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.order__item-index-text {
  font-size: 20rpx;
  font-weight: 700;
  color: $cf-accent;
}

.order__item-right {
  flex: 1;
}

.order__item-venue {
  font-size: 26rpx;
  font-weight: 700;
  color: $cf-white;
  display: block;
}

.order__item-court {
  font-size: 22rpx;
  color: $cf-text-2;
  margin-top: 4rpx;
  display: block;
}

.order__item-time-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-top: 8rpx;
}

.order__item-date {
  font-size: 22rpx;
  color: $cf-accent;
  font-weight: 600;
}

.order__item-sep {
  font-size: 20rpx;
  color: $cf-text-3;
}

.order__item-time {
  font-size: 22rpx;
  color: $cf-text-2;
}

.order__item-price {
  font-size: 28rpx;
  font-weight: 800;
  color: $cf-white;
  flex-shrink: 0;
}

// ─── Contact ─────────────────────────────────────────────────────────────────
.order__contact-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.order__contact-icon-wrap {
  width: 64rpx;
  height: 64rpx;
  background: $cf-card-2;
  border-radius: $r-md;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.order__contact-icon {
  font-size: 28rpx;
}

.order__contact-content {
  flex: 1;
}

.order__contact-label {
  font-size: 20rpx;
  color: $cf-text-2;
  display: block;
  margin-bottom: 6rpx;
}

.order__phone-input {
  font-size: 28rpx;
  color: $cf-white;
  font-weight: 600;
  background: transparent;
  height: 48rpx;
  width: 100%;
}

.order__phone-placeholder {
  color: $cf-text-3;
  font-size: 26rpx;
  font-weight: 400;
}

.order__contact-clear {
  font-size: 28rpx;
  color: $cf-text-2;
  padding: 8rpx;
}

// ─── Coupon ──────────────────────────────────────────────────────────────────
.order__coupon-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.order__coupon-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.order__coupon-icon {
  font-size: 28rpx;
}

.order__coupon-label {
  font-size: 28rpx;
  color: $cf-white;
  font-weight: 500;
}

.order__coupon-right {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.order__coupon-value {
  font-size: 26rpx;
  color: $cf-text-2;
  &--active { color: $cf-accent; font-weight: 700; }
}

.order__coupon-arrow {
  font-size: 36rpx;
  color: $cf-text-2;
}

// ─── Price breakdown ─────────────────────────────────────────────────────────
.order__price-rows {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.order__price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  &--discount {}
  &--total { margin-top: 4rpx; }
}

.order__price-label {
  font-size: 26rpx;
  color: $cf-text-2;
  &--total { color: $cf-white; font-weight: 700; font-size: 28rpx; }
}

.order__price-value {
  font-size: 26rpx;
  color: $cf-white;
  font-weight: 600;
  &--discount { color: $cf-green; }
  &--total { font-size: 36rpx; font-weight: 900; color: $cf-accent; }
}

.order__price-divider {
  height: 1rpx;
  background: $cf-line;
  margin: 4rpx 0;
}

// ─── Footer ──────────────────────────────────────────────────────────────────
.order__footer {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: $cf-surface;
  border-top: 1rpx solid $cf-line-2;
  padding-bottom: env(safe-area-inset-bottom);
}

.order__footer-inner {
  display: flex;
  align-items: center;
  padding: 20rpx 32rpx;
  gap: 20rpx;
}

.order__footer-price-wrap {
  flex: 1;
}

.order__footer-label {
  font-size: 20rpx;
  color: $cf-text-2;
  display: block;
}

.order__footer-total {
  font-size: 44rpx;
  font-weight: 900;
  color: $cf-accent;
  letter-spacing: -0.02em;
  display: block;
}

.order__pay-btn {
  background: $cf-accent;
  border-radius: $r-full;
  padding: 0 48rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  &--disabled { opacity: 0.6; }
  &:not(&--disabled):active { opacity: 0.85; }
}

.order__pay-btn-text {
  font-size: 28rpx;
  font-weight: 700;
  color: #0a1a0d;
  letter-spacing: 0.04em;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.8); }
}
</style>
