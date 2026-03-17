<template>
  <view class="login">
    <!-- Background decoration -->
    <view class="login__bg">
      <view class="login__bg-circle login__bg-circle--1" />
      <view class="login__bg-circle login__bg-circle--2" />
      <view class="login__bg-lines">
        <view v-for="i in 8" :key="i" class="login__bg-line" />
      </view>
    </view>

    <view class="login__content">
      <!-- Logo section -->
      <view class="login__hero">
        <view class="login__logo-mark">
          <text class="login__logo-icon">⊕</text>
        </view>
        <text class="login__brand">RallyAI</text>
        <text class="login__subtitle">专业网球场馆预订平台</text>
      </view>

      <!-- Features list -->
      <view class="login__features">
        <view v-for="f in features" :key="f.icon" class="login__feature-row">
          <view class="login__feature-icon-wrap">
            <cf-icon :name="f.icon" :size="28" :color="f.color" />
          </view>
          <view class="login__feature-text-wrap">
            <text class="login__feature-title">{{ f.title }}</text>
            <text class="login__feature-desc">{{ f.desc }}</text>
          </view>
        </view>
      </view>

      <!-- Login buttons -->
      <view class="login__actions">
        <button class="login__wechat-btn" open-type="getUserInfo" @getuserinfo="onWechatLogin">
          <cf-icon name="chat" :size="28" color="#fff" />
          <text class="login__wechat-text">微信一键登录</text>
        </button>
        <view class="login__divider">
          <view class="login__divider-line" />
          <text class="login__divider-text">或</text>
          <view class="login__divider-line" />
        </view>
        <view class="login__phone-btn" @tap="onPhoneLogin">
          <text class="login__phone-text">手机号登录</text>
        </view>
      </view>

      <!-- Privacy note -->
      <view class="login__privacy">
        <text class="login__privacy-text">
          登录即代表同意
          <text class="login__privacy-link" @tap="goPrivacy">《用户协议》</text>
          与
          <text class="login__privacy-link" @tap="goPrivacy">《隐私政策》</text>
        </text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import CfIcon from '@/components/ui/CfIcon.vue'

const authStore = useAuthStore()

const features = [
  { icon: 'court',    color: '#B8D430', title: '实时场地查询', desc: '多场馆同步可用时段' },
  { icon: 'star',     color: '#2E86C1', title: '秒级预订确认', desc: '锁定时段，5分钟内完成支付' },
  { icon: 'document', color: '#7B4FA0', title: '订单全程管理', desc: '预约提醒、改期、退款一键操作' },
]

async function onWechatLogin(e: any) {
  try {
      await authStore.loginWithWechat()
    uni.switchTab({ url: '/pages/index/index' })
  } catch (err) {
    uni.showToast({ title: '登录失败，请重试', icon: 'none' })
  }
}

function onPhoneLogin() {
  // Phone login flow — Phase 2
  uni.showToast({ title: '请使用微信登录', icon: 'none' })
}

function goPrivacy() {
  // Navigate to privacy page
}
</script>

<style lang="scss">
@import '@/uni.scss';

.login {
  min-height: 100vh;
  background: $cf-bg;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-end;
}

// ─── Background ──────────────────────────────────────────────────────────────
.login__bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none;
}

.login__bg-circle {
  position: absolute;
  border-radius: $r-full;
  border: 1rpx solid rgba(196, 232, 74, 0.08);
}

.login__bg-circle--1 {
  width: 800rpx; height: 800rpx; top: -300rpx; left: -200rpx;
  background: radial-gradient(circle at center, rgba(45,139,87,0.18) 0%, transparent 65%);
}
.login__bg-circle--2 {
  width: 500rpx; height: 500rpx; top: -100rpx; right: -150rpx;
  background: radial-gradient(circle at center, rgba(46,134,193,0.14) 0%, transparent 65%);
}

.login__bg-lines {
  position: absolute;
  top: 80rpx;
  left: 0;
  right: 0;
  height: 600rpx;
  display: flex;
  flex-direction: column;
  gap: 60rpx;
  opacity: 0.04;
}

.login__bg-line {
  height: 1rpx;
  background: $cf-accent;
  width: 100%;
}

// ─── Content ─────────────────────────────────────────────────────────────────
.login__content {
  position: relative;
  z-index: 2;
  width: 100%;
  padding: 0 48rpx;
  padding-bottom: 80rpx;
  padding-bottom: calc(80rpx + env(safe-area-inset-bottom));
}

// ─── Hero ─────────────────────────────────────────────────────────────────────
.login__hero {
  padding-top: 160rpx;
  padding-bottom: 64rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.login__logo-mark {
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, $cf-green, $cf-blue);
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32rpx;
}

.login__logo-icon {
  font-size: 52rpx;
  color: #0a1a0d;
}

.login__brand {
  font-size: 64rpx;
  font-weight: 900;
  color: $cf-white;
  letter-spacing: -0.03em;
  display: block;
}

.login__subtitle {
  font-size: 26rpx;
  color: $cf-text-2;
  margin-top: 8rpx;
  display: block;
  letter-spacing: 0.04em;
}

// ─── Features ────────────────────────────────────────────────────────────────
.login__features {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 64rpx;
}

.login__feature-row {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.login__feature-icon-wrap {
  width: 72rpx;
  height: 72rpx;
  background: $cf-card;
  border-radius: $r-md;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1rpx solid $cf-line;
  flex-shrink: 0;
}

.login__feature-icon {
  font-size: 32rpx;
}

.login__feature-title {
  font-size: 26rpx;
  font-weight: 600;
  color: $cf-white;
  display: block;
}

.login__feature-desc {
  font-size: 22rpx;
  color: $cf-text-2;
  margin-top: 4rpx;
  display: block;
}

// ─── Actions ─────────────────────────────────────────────────────────────────
.login__actions {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 32rpx;
}

.login__wechat-btn {
  width: 100%;
  height: 100rpx;
  background: linear-gradient(135deg, $cf-green, $cf-blue);
  border-radius: $r-full;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  border: none;
  padding: 0;
  &::after { border: none; }
  &:active { opacity: 0.85; }
}

.login__wechat-icon {
  font-size: 36rpx;
}

.login__wechat-text {
  font-size: 30rpx;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.02em;
}

.login__divider {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.login__divider-line {
  flex: 1;
  height: 1rpx;
  background: $cf-line;
}

.login__divider-text {
  font-size: 22rpx;
  color: $cf-text-3;
}

.login__phone-btn {
  width: 100%;
  height: 100rpx;
  background: transparent;
  border-radius: $r-full;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1.5rpx solid $cf-line-2;
  &:active { background: $cf-card; }
}

.login__phone-text {
  font-size: 28rpx;
  color: $cf-text-2;
  font-weight: 500;
}

// ─── Privacy ─────────────────────────────────────────────────────────────────
.login__privacy {
  text-align: center;
}

.login__privacy-text {
  font-size: 20rpx;
  color: $cf-text-3;
}

.login__privacy-link {
  color: $cf-text-2;
  text-decoration: underline;
}
</style>
