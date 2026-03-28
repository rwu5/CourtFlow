<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">场地管理</text>
      <CfButton type="primary" size="sm" icon="plus" @click="goCreate">新建</CfButton>
    </view>

    <scroll-view scroll-y class="content">
      <CfEmpty v-if="!courts.length" icon="court" text="暂无场地" />
      <view
        v-for="court in courts"
        :key="court.id"
        class="court-item cf-glass-card"
        @click="goEdit(court.id)"
      >
        <view class="court-item__top">
          <text class="court-item__name">{{ court.name }}</text>
          <view :class="['cf-badge', court.is_active ? 'cf-badge--green' : 'cf-badge--grey']">
            {{ court.is_active ? '启用' : '停用' }}
          </view>
        </view>
        <view class="court-item__tags">
          <text v-if="court.surface" class="court-item__tag">{{ surfaceLabel(court.surface) }}</text>
          <text class="court-item__tag">{{ court.is_indoor ? '室内' : '室外' }}</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfButton from '@/components/ui/CfButton.vue'
import CfEmpty from '@/components/ui/CfEmpty.vue'
import type { Court } from '@/types'
import { listCourts } from '@/api/courts'

const venueId = ref('')
const courts = ref<Court[]>([])

const surfaceLabels: Record<string, string> = {
  hard: '硬地', clay: '红土', grass: '草地', synthetic: '人工',
}
function surfaceLabel(s: string) { return surfaceLabels[s] ?? s }

onMounted(() => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1] as any
  venueId.value = page?.$page?.options?.venueId || page?.options?.venueId || ''
})

onShow(async () => {
  if (venueId.value) {
    try { courts.value = await listCourts(venueId.value) } catch {}
  }
})

function goCreate() {
  uni.navigateTo({ url: `/packages/venue/court-edit/index?venueId=${venueId.value}` })
}

function goEdit(courtId: string) {
  uni.navigateTo({ url: `/packages/venue/court-edit/index?venueId=${venueId.value}&id=${courtId}` })
}
</script>

<style lang="scss" scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  padding-top: calc(env(safe-area-inset-top) + 24rpx);
  &__back { padding: 8rpx; }
  &__title { font-size: 32rpx; font-weight: 700; color: $cf-white; flex: 1; margin-left: 8rpx; }
}

.content {
  padding: $sp-md;
  height: calc(100vh - 160rpx - env(safe-area-inset-top));
}

.court-item {
  padding: $sp-md;
  margin-bottom: $sp-sm;

  &__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8rpx;
  }

  &__name { font-size: 28rpx; font-weight: 700; color: $cf-white; }

  &__tags { display: flex; gap: 8rpx; }

  &__tag {
    font-size: 22rpx;
    color: $cf-text-2;
    background: $cf-glass-bg;
    padding: 4rpx 12rpx;
    border-radius: $r-full;
  }
}
</style>
