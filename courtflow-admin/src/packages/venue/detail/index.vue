<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">{{ venue?.short_name || venue?.name || '场馆详情' }}</text>
      <view class="page-header__action" @click="goSettings">
        <CfIcon name="settings" :size="20" color="rgba(255,255,255,0.6)" />
      </view>
    </view>

    <scroll-view scroll-y class="content">
      <!-- Photos -->
      <view class="section">
        <view class="section__header">
          <text class="section__title">场馆照片</text>
          <view class="section__link" @click="goPhotos">
            <text>管理</text>
            <CfIcon name="chevron-right" :size="14" color="rgba(255,255,255,0.4)" />
          </view>
        </view>
        <scroll-view v-if="media.length" scroll-x class="photo-scroll">
          <view class="photo-list">
            <image
              v-for="m in media"
              :key="m.id"
              :src="m.url"
              class="photo-item"
              mode="aspectFill"
            />
          </view>
        </scroll-view>
        <view v-else class="photo-empty cf-glass-card">
          <CfIcon name="image" :size="32" color="rgba(255,255,255,0.2)" />
          <text class="photo-empty__text">暂无照片</text>
        </view>
      </view>

      <!-- Courts -->
      <view class="section">
        <view class="section__header">
          <text class="section__title">场地</text>
          <CfButton type="ghost" size="sm" icon="plus" @click="goCreateCourt">新建</CfButton>
        </view>
        <CfEmpty v-if="!courts.length" icon="court" text="暂无场地" />
        <view
          v-for="court in courts"
          :key="court.id"
          class="court-item cf-glass-card"
          @click="goCourtDetail(court.id)"
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
            <text class="court-item__tag">{{ court.slot_duration_minutes }}分钟/时段</text>
          </view>
        </view>
      </view>

      <!-- Facilities -->
      <view class="section">
        <view class="section__header">
          <text class="section__title">设施</text>
          <view class="section__link" @click="goFacilities">
            <text>管理</text>
            <CfIcon name="chevron-right" :size="14" color="rgba(255,255,255,0.4)" />
          </view>
        </view>
        <view v-if="facilities.length" class="facility-chips">
          <view v-for="f in facilities" :key="f.id" class="facility-chip">
            {{ f.label }}
          </view>
        </view>
        <view v-else class="empty-hint">
          <text class="empty-hint__text">暂无设施信息</text>
        </view>
      </view>

      <!-- Coaches (placeholder) -->
      <view class="section">
        <view class="section__header">
          <text class="section__title">教练</text>
        </view>
        <view class="empty-hint">
          <text class="empty-hint__text">即将上线</text>
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
import type { Venue, VenueMedia, VenueFacility, Court } from '@/types'
import { getVenue, listVenueMedia, listVenueFacilities } from '@/api/venues'
import { listCourts } from '@/api/courts'

const venueId = ref('')
const venue = ref<Venue | null>(null)
const media = ref<VenueMedia[]>([])
const courts = ref<Court[]>([])
const facilities = ref<VenueFacility[]>([])

const surfaceLabels: Record<string, string> = {
  hard: '硬地', clay: '红土', grass: '草地', synthetic: '人工',
}
function surfaceLabel(s: string) { return surfaceLabels[s] ?? s }

onMounted(() => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1] as any
  venueId.value = page?.$page?.options?.id || page?.options?.id || ''
})

onShow(async () => {
  if (!venueId.value) return
  try {
    const [v, m, c, f] = await Promise.all([
      getVenue(venueId.value),
      listVenueMedia(venueId.value),
      listCourts(venueId.value),
      listVenueFacilities(venueId.value),
    ])
    venue.value = v
    media.value = m
    courts.value = c
    facilities.value = f
  } catch (e) {
    console.error('Failed to load venue detail', e)
  }
})

function goSettings() {
  uni.navigateTo({ url: `/packages/venue/edit/index?id=${venueId.value}` })
}

function goPhotos() {
  uni.navigateTo({ url: `/packages/venue/photos/index?venueId=${venueId.value}` })
}

function goFacilities() {
  uni.navigateTo({ url: `/packages/venue/facilities/index?venueId=${venueId.value}` })
}

function goCreateCourt() {
  uni.navigateTo({ url: `/packages/venue/court-edit/index?venueId=${venueId.value}` })
}

function goCourtDetail(courtId: string) {
  uni.navigateTo({ url: `/packages/venue/court-detail/index?venueId=${venueId.value}&courtId=${courtId}` })
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
  &__action { padding: 8rpx; }
}

.content {
  padding: 0 $sp-md $sp-xl;
  height: calc(100vh - 120rpx - env(safe-area-inset-top));
}

.section {
  margin-bottom: $sp-lg;

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: $sp-sm;
  }

  &__title {
    font-size: 28rpx;
    font-weight: 700;
    color: $cf-white;
  }

  &__link {
    display: flex;
    align-items: center;
    gap: 4rpx;
    font-size: 24rpx;
    color: $cf-text-2;
  }
}

.photo-scroll {
  white-space: nowrap;
}

.photo-list {
  display: inline-flex;
  gap: $sp-sm;
}

.photo-item {
  width: 200rpx;
  height: 200rpx;
  border-radius: $r-md;
  flex-shrink: 0;
}

.photo-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $sp-lg;
  gap: $sp-xs;

  &__text {
    font-size: 24rpx;
    color: $cf-text-3;
  }
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

.facility-chips {
  display: flex;
  flex-wrap: wrap;
  gap: $sp-xs;
}

.facility-chip {
  font-size: 24rpx;
  color: $cf-text-2;
  background: $cf-glass-bg;
  border: 0.5px solid $cf-glass-border;
  padding: 8rpx 20rpx;
  border-radius: $r-full;
}

.empty-hint {
  padding: $sp-md 0;

  &__text {
    font-size: 24rpx;
    color: $cf-text-3;
  }
}
</style>
