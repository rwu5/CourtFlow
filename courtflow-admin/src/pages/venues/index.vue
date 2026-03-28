<template>
  <view class="cf-page">
    <view class="page-header">
      <text class="page-header__title">场馆管理</text>
      <CfButton type="primary" size="sm" icon="plus" @click="goCreate">新建</CfButton>
    </view>

    <scroll-view scroll-y class="content">
      <CfEmpty v-if="!venues.length" icon="building" text="暂无场馆，点击右上角新建" />
      <view
        v-for="venue in venues"
        :key="venue.id"
        class="venue-card cf-glass-card"
        @click="goDetail(venue.id)"
      >
        <view class="venue-card__top">
          <text class="venue-card__name">{{ venue.name }}</text>
          <view :class="['cf-badge', venue.is_active ? 'cf-badge--green' : 'cf-badge--grey']">
            {{ venue.is_active ? '营业中' : '已关闭' }}
          </view>
        </view>
        <view class="venue-card__row">
          <CfIcon name="location" :size="14" color="rgba(255,255,255,0.4)" />
          <text class="venue-card__addr">{{ venue.address }}</text>
        </view>
        <view class="venue-card__row">
          <CfIcon name="clock" :size="14" color="rgba(255,255,255,0.4)" />
          <text class="venue-card__time">{{ venue.open_time }} - {{ venue.close_time }}</text>
        </view>
      </view>
    </scroll-view>

    <CfTabBar current="pages/venues/index" />
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfButton from '@/components/ui/CfButton.vue'
import CfEmpty from '@/components/ui/CfEmpty.vue'
import CfTabBar from '@/components/ui/CfTabBar.vue'
import type { Venue } from '@/types'
import { listVenues } from '@/api/venues'

const venues = ref<Venue[]>([])

onShow(async () => {
  try {
    venues.value = await listVenues()
  } catch (e) {
    console.error('Failed to load venues', e)
  }
})

function goCreate() {
  uni.navigateTo({ url: '/packages/venue/edit/index' })
}

function goDetail(id: string) {
  uni.navigateTo({ url: `/packages/venue/detail/index?id=${id}` })
}
</script>

<style lang="scss" scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  padding-top: calc(env(safe-area-inset-top) + 24rpx);

  &__title {
    font-size: 36rpx;
    font-weight: 800;
    color: $cf-white;
  }
}

.content {
  height: calc(100vh - 160rpx - env(safe-area-inset-top) - 100rpx);
  padding: 0 $sp-md;
}

.venue-card {
  padding: $sp-md;
  margin-bottom: $sp-sm;

  &__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12rpx;
  }

  &__name {
    font-size: 30rpx;
    font-weight: 700;
    color: $cf-white;
  }

  &__row {
    display: flex;
    align-items: center;
    gap: 8rpx;
    margin-bottom: 8rpx;
  }

  &__addr,
  &__time {
    font-size: 24rpx;
    color: $cf-text-2;
  }

}
</style>
