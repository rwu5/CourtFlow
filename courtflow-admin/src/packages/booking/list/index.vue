<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">预约管理</text>
      <view class="page-header__action" />
    </view>

    <!-- Status filter chips -->
    <scroll-view scroll-x class="filter-bar">
      <view class="filter-chips">
        <view
          v-for="s in statusFilters"
          :key="s.value"
          :class="['chip', filterStatus === s.value && 'chip--active']"
          @click="filterStatus = s.value; page = 1; load()"
        >
          <text class="chip__text">{{ s.label }}</text>
        </view>
      </view>
    </scroll-view>

    <!-- Date filter -->
    <view class="date-bar">
      <picker mode="date" :value="filterDate" @change="onDateChange">
        <view class="date-bar__picker">
          <CfIcon name="calendar" :size="16" color="rgba(255,255,255,0.5)" />
          <text class="date-bar__text">{{ filterDate || '全部日期' }}</text>
        </view>
      </picker>
      <view v-if="filterDate" class="date-bar__clear" @click="filterDate = ''; page = 1; load()">
        <CfIcon name="close" :size="14" color="rgba(255,255,255,0.4)" />
      </view>
    </view>

    <scroll-view scroll-y class="content" @scrolltolower="loadMore">
      <CfEmpty v-if="!loading && !reservations.length" icon="document" text="暂无预约记录" />
      <view
        v-for="r in reservations"
        :key="r.id"
        class="booking-card cf-glass-card"
        @click="goDetail(r.id)"
      >
        <view class="booking-card__top">
          <text class="booking-card__court">{{ r.court_name }}</text>
          <view :class="['cf-badge', badgeClass(r.status)]">
            {{ statusLabel(r.status) }}
          </view>
        </view>
        <view class="booking-card__time">
          <CfIcon name="clock" :size="14" color="rgba(255,255,255,0.4)" />
          <text class="booking-card__time-text">{{ formatSlot(r.slot_start_at, r.slot_end_at) }}</text>
        </view>
        <view class="booking-card__bottom">
          <text class="booking-card__user">
            <CfIcon name="person" :size="14" color="rgba(255,255,255,0.4)" />
            {{ r.user_nickname || r.user_phone || '未知用户' }}
          </text>
          <text class="booking-card__price">&yen;{{ (r.amount_cents / 100).toFixed(0) }}</text>
        </view>
      </view>

      <view v-if="hasMore" class="load-more" @click="loadMore">
        <text class="load-more__text">{{ loading ? '加载中...' : '加载更多' }}</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfEmpty from '@/components/ui/CfEmpty.vue'
import type { Reservation } from '@/types'
import { listReservations } from '@/api/reservations'

const reservations = ref<Reservation[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = 20

// Filters
const filterStatus = ref('')
const filterDate = ref('')
const preVenueId = ref('')
const preCourtId = ref('')

const hasMore = computed(() => reservations.value.length < total.value)

const statusFilters = [
  { value: '', label: '全部' },
  { value: 'confirmed', label: '已确认' },
  { value: 'checked_in', label: '已签到' },
  { value: 'held', label: '锁定中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
  { value: 'admin_cancelled', label: '管理取消' },
  { value: 'no_show', label: '未到场' },
]

const statusLabels: Record<string, string> = {
  held: '锁定中', pending_payment: '待支付', payment_failed: '支付失败',
  confirmed: '已确认', checked_in: '已签到', completed: '已完成',
  cancelled: '已取消', admin_cancelled: '管理取消', no_show: '未到场',
  refunded: '已退款', partially_refunded: '部分退款',
}

function statusLabel(s: string) { return statusLabels[s] ?? s }

function badgeClass(s: string): string {
  if (['confirmed', 'checked_in'].includes(s)) return 'cf-badge--green'
  if (['held', 'pending_payment'].includes(s)) return 'cf-badge--amber'
  if (['completed'].includes(s)) return 'cf-badge--blue'
  return 'cf-badge--grey'
}

function formatSlot(start: string, end: string): string {
  const s = new Date(start)
  const e = new Date(end)
  const date = `${s.getMonth() + 1}/${s.getDate()}`
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date} ${pad(s.getHours())}:${pad(s.getMinutes())} - ${pad(e.getHours())}:${pad(e.getMinutes())}`
}

onMounted(() => {
  const pages = getCurrentPages()
  const p = pages[pages.length - 1] as any
  const opts = p?.$page?.options || p?.options || {}
  preVenueId.value = opts.venue_id || ''
  preCourtId.value = opts.court_id || ''
})

onShow(() => {
  page.value = 1
  load()
})

async function load() {
  loading.value = true
  try {
    const params: Record<string, any> = { page: page.value, page_size: pageSize }
    if (preVenueId.value) params.venue_id = preVenueId.value
    if (preCourtId.value) params.court_id = preCourtId.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterDate.value) {
      params.date_from = filterDate.value
      params.date_to = filterDate.value
    }
    const res = await listReservations(params)
    if (page.value === 1) {
      reservations.value = res.items
    } else {
      reservations.value = [...reservations.value, ...res.items]
    }
    total.value = res.total
  } catch (e) {
    console.error('Failed to load reservations', e)
  } finally {
    loading.value = false
  }
}

function loadMore() {
  if (loading.value || !hasMore.value) return
  page.value++
  load()
}

function onDateChange(e: any) {
  filterDate.value = e.detail.value
  page.value = 1
  load()
}

function goDetail(id: string) {
  uni.navigateTo({ url: `/packages/booking/detail/index?id=${id}` })
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
  &__action { width: 40rpx; }
}

.filter-bar {
  padding: 0 $sp-md;
  white-space: nowrap;
  margin-bottom: $sp-xs;
}

.filter-chips {
  display: inline-flex;
  gap: 12rpx;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 8rpx 20rpx;
  border-radius: $r-full;
  background: $cf-glass-bg;
  border: 0.5px solid $cf-glass-border;

  &--active {
    background: rgba($cf-green, 0.25);
    border-color: $cf-green;
  }

  &__text {
    font-size: 24rpx;
    color: $cf-text-2;
  }

  &--active &__text {
    color: $cf-green;
    font-weight: 600;
  }
}

.date-bar {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: $sp-xs $sp-md;

  &__picker {
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding: 8rpx 16rpx;
    background: $cf-glass-bg;
    border-radius: $r-full;
    border: 0.5px solid $cf-glass-border;
  }

  &__text {
    font-size: 24rpx;
    color: $cf-text-2;
  }

  &__clear {
    padding: 8rpx;
  }
}

.content {
  padding: 0 $sp-md $sp-xl;
  height: calc(100vh - 320rpx - env(safe-area-inset-top));
}

.booking-card {
  padding: $sp-md;
  margin-bottom: $sp-sm;

  &__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8rpx;
  }

  &__court {
    font-size: 28rpx;
    font-weight: 700;
    color: $cf-white;
  }

  &__time {
    display: flex;
    align-items: center;
    gap: 8rpx;
    margin-bottom: 8rpx;
  }

  &__time-text {
    font-size: 24rpx;
    color: $cf-text-2;
  }

  &__bottom {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  &__user {
    display: flex;
    align-items: center;
    gap: 6rpx;
    font-size: 24rpx;
    color: $cf-text-2;
  }

  &__price {
    font-size: 28rpx;
    font-weight: 700;
    color: $cf-lime;
  }
}

.load-more {
  text-align: center;
  padding: $sp-md;

  &__text {
    font-size: 24rpx;
    color: $cf-text-2;
  }
}
</style>
