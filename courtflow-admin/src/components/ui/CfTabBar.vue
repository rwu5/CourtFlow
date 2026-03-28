<template>
  <view class="tab-bar">
    <view class="tab-bar__inner">
      <view
        v-for="tab in tabs"
        :key="tab.path"
        class="tab-bar__item"
        :class="{ 'tab-bar__item--active': current === tab.path }"
        @click="switchTab(tab.path)"
      >
        <CfIcon
          :name="tab.icon"
          :size="22"
          :color="current === tab.path ? '#B8D430' : 'rgba(255,255,255,0.4)'"
        />
        <text class="tab-bar__label">{{ tab.label }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import CfIcon from './CfIcon.vue'

defineProps<{ current: string }>()

const tabs = [
  { path: 'pages/index/index', icon: 'chart-bar', label: '概览' },
  { path: 'pages/venues/index', icon: 'building', label: '场馆' },
  { path: 'pages/bookings/index', icon: 'document', label: '预约' },
  { path: 'pages/my/index', icon: 'person', label: '我的' },
]

function switchTab(path: string) {
  uni.switchTab({ url: `/${path}` })
}
</script>

<style lang="scss" scoped>
.tab-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  padding-bottom: env(safe-area-inset-bottom);
  background: rgba(8, 14, 11, 0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-top: 0.5px solid rgba(255, 255, 255, 0.08);

  &__inner {
    display: flex;
    justify-content: space-around;
    align-items: center;
    height: 100rpx;
  }

  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4rpx;
    flex: 1;

    &--active {
      .tab-bar__label {
        color: #B8D430;
      }
    }
  }

  &__label {
    font-size: 20rpx;
    color: rgba(255, 255, 255, 0.4);
  }
}
</style>
