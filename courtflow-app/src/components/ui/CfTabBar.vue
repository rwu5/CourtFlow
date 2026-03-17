<template>
  <view class="tab-bar">
    <view class="tab-bar__blur" />
    <view class="tab-bar__border" />
    <view class="tab-bar__inner">
      <view
        v-for="tab in tabs"
        :key="tab.page"
        class="tab-bar__item"
        :class="{ 'tab-bar__item--active': current === tab.page }"
        @tap="switchTab(tab.page)"
      >
        <!-- Icon container with glow -->
        <view class="tab-bar__icon-wrap" :class="{ 'tab-bar__icon-wrap--active': current === tab.page }">
          <view class="tab-bar__icon-glow" v-if="current === tab.page" />
          <view class="tab-bar__svg" v-html="getIcon(tab.icon, current === tab.page)" />
        </view>
        <text class="tab-bar__label" :class="{ 'tab-bar__label--active': current === tab.page }">
          {{ tab.label }}
        </text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  current: string
}>()

const tabs = [
  { page: '/pages/index/index',   icon: 'home',    label: '主页' },
  { page: '/pages/courts/index',  icon: 'court',   label: '场地' },
  { page: '/pages/courses/index', icon: 'courses', label: '课程' },
  { page: '/pages/my/index',      icon: 'person',  label: '我的' },
]

// SVG paths — Heroicons outline style, 24×24 viewBox
const iconPaths: Record<string, string> = {
  home: `<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955a1.126 1.126 0 011.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/>`,
  court: `<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6"/>`,
  courses: `<path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5"/>`,
  person: `<path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>`,
}

function getIcon(name: string, active: boolean): string {
  const path = iconPaths[name] || ''
  const color = active ? '#B8D430' : 'rgba(255,255,255,0.35)'
  const sw = active ? '1.8' : '1.5'
  return `<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="${sw}" style="display:block;transition:all 0.25s">${path}</svg>`
}

function switchTab(page: string) {
  uni.switchTab({ url: page })
}
</script>

<style lang="scss">
@import '@/uni.scss';

.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 999;
  padding-bottom: env(safe-area-inset-bottom);
}

.tab-bar__blur {
  position: absolute;
  inset: 0;
  background: rgba(8, 14, 11, 0.82);
  backdrop-filter: blur(24px) saturate(1.4);
  -webkit-backdrop-filter: blur(24px) saturate(1.4);
}

.tab-bar__border {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 0.5px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(184, 212, 48, 0.25) 30%,
    rgba(45, 139, 87, 0.35) 50%,
    rgba(184, 212, 48, 0.25) 70%,
    transparent 100%
  );
}

.tab-bar__inner {
  position: relative;
  display: flex;
  align-items: stretch;
  height: 108rpx;
}

.tab-bar__item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
  position: relative;
  padding-top: 12rpx;
  transition: opacity 0.2s;
  &:active { opacity: 0.75; }
}

.tab-bar__icon-wrap {
  position: relative;
  width: 52rpx;
  height: 52rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: $r-sm;
  transition: background 0.25s;

  &--active {
    background: rgba(184, 212, 48, 0.10);
  }
}

.tab-bar__icon-glow {
  position: absolute;
  inset: -4rpx;
  border-radius: $r-md;
  background: radial-gradient(circle at center, rgba(184, 212, 48, 0.20) 0%, transparent 70%);
  pointer-events: none;
}

.tab-bar__svg {
  line-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-bar__label {
  font-size: 18rpx;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.35);
  letter-spacing: 0.02em;
  transition: color 0.25s;

  &--active {
    color: $cf-lime;
    font-weight: 600;
  }
}

</style>
