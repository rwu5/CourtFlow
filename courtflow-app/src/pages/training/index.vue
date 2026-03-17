<template>
  <view class="training">
    <view class="training__statusbar" />

    <view class="training__content">
      <!-- Header -->
      <view class="training__header">
        <text class="training__header-title">训练</text>
      </view>

      <!-- Coming soon card -->
      <view class="training__soon-card">
        <view class="training__soon-bg">
          <view v-for="i in 5" :key="i" class="training__soon-ring" :style="{ width: `${200 + i * 120}rpx`, height: `${200 + i * 120}rpx`, opacity: 0.08 - i * 0.01 }" />
        </view>
        <view class="training__soon-icon-wrap">
          <text class="training__soon-icon">🎾</text>
        </view>
        <text class="training__soon-title">即将上线</text>
        <text class="training__soon-desc">AI 训练计划、视频分析、教练匹配、对练组队…等你来玩</text>
        <view class="training__soon-features">
          <view v-for="f in upcomingFeatures" :key="f" class="training__soon-feature">
            <view class="training__soon-feature-dot" />
            <text class="training__soon-feature-text">{{ f }}</text>
          </view>
        </view>
        <view class="training__notify-btn" @tap="notifyMe">
          <text class="training__notify-text">上线提醒我</text>
        </view>
      </view>
    </view>

    <view style="height: 120rpx;" />
  </view>
</template>

<script setup lang="ts">
const upcomingFeatures = [
  'AI 挥拍动作分析',
  '个性化训练计划',
  '匹配同水平球友',
  '专业教练一对一',
  '赛事报名与成绩',
]

function notifyMe() {
  uni.showToast({ title: '已开启上线提醒', icon: 'success' })
}
</script>

<style lang="scss">
@import '@/uni.scss';

.training {
  background: $cf-bg;
  min-height: 100vh;
}

.training__statusbar {
  height: var(--status-bar-height, 44px);
  background: $cf-bg;
}

.training__content {
  padding: 0 32rpx;
}

.training__header {
  padding: 16rpx 8rpx 32rpx;
}

.training__header-title {
  font-size: 40rpx;
  font-weight: 800;
  color: $cf-white;
  letter-spacing: -0.02em;
  display: block;
}

// ─── Coming soon card ────────────────────────────────────────────────────────
.training__soon-card {
  background: $cf-card;
  border-radius: $r-xl;
  border: 1rpx solid $cf-line;
  padding: 60rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.training__soon-bg {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.training__soon-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: $r-full;
  border: 1rpx solid $cf-accent;
}

.training__soon-icon-wrap {
  width: 140rpx;
  height: 140rpx;
  background: $cf-accent-dim;
  border-radius: $r-full;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid rgba(196,232,74,0.25);
  margin-bottom: 32rpx;
  position: relative;
  z-index: 2;
}

.training__soon-icon {
  font-size: 64rpx;
}

.training__soon-title {
  font-size: 52rpx;
  font-weight: 900;
  color: $cf-white;
  letter-spacing: -0.03em;
  display: block;
  margin-bottom: 20rpx;
  position: relative;
  z-index: 2;
}

.training__soon-desc {
  font-size: 26rpx;
  color: $cf-text-2;
  line-height: 1.6;
  display: block;
  margin-bottom: 40rpx;
  position: relative;
  z-index: 2;
}

.training__soon-features {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  width: 100%;
  margin-bottom: 48rpx;
  position: relative;
  z-index: 2;
}

.training__soon-feature {
  display: flex;
  align-items: center;
  gap: 16rpx;
  text-align: left;
  background: $cf-card-2;
  border-radius: $r-md;
  padding: 16rpx 20rpx;
  border: 1rpx solid $cf-line;
}

.training__soon-feature-dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: $r-full;
  background: $cf-accent;
  flex-shrink: 0;
}

.training__soon-feature-text {
  font-size: 26rpx;
  color: $cf-text-2;
}

.training__notify-btn {
  background: $cf-accent;
  border-radius: $r-full;
  padding: 18rpx 64rpx;
  position: relative;
  z-index: 2;
  &:active { opacity: 0.85; }
}

.training__notify-text {
  font-size: 28rpx;
  font-weight: 700;
  color: #0a1a0d;
  letter-spacing: 0.04em;
}
</style>
