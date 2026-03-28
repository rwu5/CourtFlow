<template>
  <view class="cf-page">
    <view class="page-header">
      <text class="page-header__title">定价管理</text>
      <CfButton type="primary" size="sm" icon="plus" @click="goCreate">新建</CfButton>
    </view>

    <!-- Venue filter -->
    <view class="venue-bar" v-if="venues.length > 1">
      <scroll-view scroll-x class="venue-bar__scroll">
        <view class="venue-chips">
          <view
            :class="['chip', !filterVenueId && 'chip--active']"
            @click="filterVenueId = ''; filterCourtId = ''; load()"
          >
            <text class="chip__text">全部场馆</text>
          </view>
          <view
            v-for="v in venues"
            :key="v.id"
            :class="['chip', filterVenueId === v.id && 'chip--active']"
            @click="filterVenueId = v.id; filterCourtId = ''; loadCourts(); load()"
          >
            <text class="chip__text">{{ v.short_name || v.name }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- Court filter (shown when venue selected) -->
    <view class="court-bar" v-if="filterVenueId && courts.length">
      <scroll-view scroll-x class="court-bar__scroll">
        <view class="court-chips">
          <view
            :class="['chip chip--sm', !filterCourtId && 'chip--active']"
            @click="filterCourtId = ''; load()"
          >
            <text class="chip__text">全部场地</text>
          </view>
          <view
            v-for="c in courts"
            :key="c.id"
            :class="['chip chip--sm', filterCourtId === c.id && 'chip--active']"
            @click="filterCourtId = c.id; load()"
          >
            <text class="chip__text">{{ c.name }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- Status filter -->
    <scroll-view scroll-x class="filter-bar">
      <view class="filter-chips">
        <view
          v-for="s in statusFilters"
          :key="s.value"
          :class="['chip chip--sm', filterActive === s.value && 'chip--active']"
          @click="filterActive = s.value; load()"
        >
          <text class="chip__text">{{ s.label }}</text>
        </view>
      </view>
    </scroll-view>

    <scroll-view scroll-y class="content">
      <CfEmpty v-if="!filteredRules.length" icon="money" text="暂无定价规则" />
      <view
        v-for="rule in filteredRules"
        :key="rule.id"
        class="rule-card cf-glass-card"
        @click="goEdit(rule.id)"
      >
        <view class="rule-card__top">
          <view class="rule-card__info">
            <text class="rule-card__name">{{ rule.name }}</text>
            <text v-if="!filterVenueId" class="rule-card__venue">{{ venueNameMap[rule.venue_id] || '' }}</text>
            <text v-if="rule.court_id" class="rule-card__court">{{ courtNameMap[rule.court_id] || '指定场地' }}</text>
          </view>
          <view :class="['cf-badge', rule.is_active ? 'cf-badge--green' : 'cf-badge--grey']">
            {{ rule.is_active ? '生效中' : '已停用' }}
          </view>
        </view>
        <view class="rule-card__price">
          <text class="rule-card__amount">&yen;{{ (rule.amount_cents / 100).toFixed(0) }}</text>
          <text v-if="rule.original_amount_cents" class="rule-card__original">
            &yen;{{ (rule.original_amount_cents / 100).toFixed(0) }}
          </text>
        </view>
        <view class="rule-card__meta">
          <text v-if="rule.weekdays" class="rule-card__tag">
            {{ formatWeekdays(rule.weekdays) }}
          </text>
          <text v-if="rule.time_from && rule.time_to" class="rule-card__tag">
            {{ rule.time_from }} - {{ rule.time_to }}
          </text>
          <text class="rule-card__tag">优先级 {{ rule.priority }}</text>
        </view>
      </view>
    </scroll-view>

    <CfTabBar current="pages/pricing/index" />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import CfButton from '@/components/ui/CfButton.vue'
import CfEmpty from '@/components/ui/CfEmpty.vue'
import CfTabBar from '@/components/ui/CfTabBar.vue'
import type { PricingRule, Venue, Court } from '@/types'
import { listPricingRules } from '@/api/pricing'
import { listVenues } from '@/api/venues'
import { listCourts } from '@/api/courts'

const rules = ref<PricingRule[]>([])
const venues = ref<Venue[]>([])
const courts = ref<Court[]>([])

// Filters
const filterVenueId = ref('')
const filterCourtId = ref('')
const filterActive = ref<'' | 'active' | 'inactive'>('')

// Name lookup maps
const venueNameMap = ref<Record<string, string>>({})
const courtNameMap = ref<Record<string, string>>({})

const statusFilters = [
  { value: '', label: '全部' },
  { value: 'active', label: '生效中' },
  { value: 'inactive', label: '已停用' },
]

const filteredRules = computed(() => {
  if (!filterActive.value) return rules.value
  return rules.value.filter(r =>
    filterActive.value === 'active' ? r.is_active : !r.is_active,
  )
})

const weekdayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

function formatWeekdays(wd: string): string {
  return wd.split(',').map(d => weekdayNames[parseInt(d)] ?? d).join(' ')
}

onMounted(async () => {
  try {
    venues.value = await listVenues()
    const map: Record<string, string> = {}
    venues.value.forEach(v => { map[v.id] = v.short_name || v.name })
    venueNameMap.value = map

    // Load all courts for name lookup
    const courtMap: Record<string, string> = {}
    for (const v of venues.value) {
      const cts = await listCourts(v.id)
      cts.forEach(c => { courtMap[c.id] = c.name })
    }
    courtNameMap.value = courtMap
  } catch {}
})

onShow(() => { load() })

async function load() {
  try {
    const params: Record<string, string> = {}
    if (filterVenueId.value) params.venue_id = filterVenueId.value
    if (filterCourtId.value) params.court_id = filterCourtId.value
    rules.value = await listPricingRules(params)
  } catch (e) {
    console.error('Failed to load pricing rules', e)
  }
}

async function loadCourts() {
  if (!filterVenueId.value) {
    courts.value = []
    return
  }
  try {
    courts.value = await listCourts(filterVenueId.value)
  } catch {
    courts.value = []
  }
}

function goCreate() {
  const params: string[] = []
  if (filterVenueId.value) params.push(`venue_id=${filterVenueId.value}`)
  if (filterCourtId.value) params.push(`court_id=${filterCourtId.value}`)
  const qs = params.length ? `?${params.join('&')}` : ''
  uni.navigateTo({ url: `/packages/pricing/edit/index${qs}` })
}

function goEdit(id: string) {
  uni.navigateTo({ url: `/packages/pricing/edit/index?id=${id}` })
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
    font-size: 34rpx;
    font-weight: 700;
    color: $cf-white;
  }
}

.venue-bar, .court-bar {
  padding: 0 $sp-md;
  margin-bottom: $sp-xs;

  &__scroll {
    white-space: nowrap;
  }
}

.venue-chips, .court-chips, .filter-chips {
  display: inline-flex;
  gap: 12rpx;
}

.filter-bar {
  padding: 0 $sp-md;
  white-space: nowrap;
  margin-bottom: $sp-xs;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 8rpx 20rpx;
  border-radius: $r-full;
  background: $cf-glass-bg;
  border: 0.5px solid $cf-glass-border;

  &--sm {
    padding: 6rpx 16rpx;
  }

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

.content {
  height: calc(100vh - 360rpx - env(safe-area-inset-top) - 100rpx);
  padding: 0 $sp-md;
}

.rule-card {
  padding: $sp-md;
  margin-bottom: $sp-sm;

  &__top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 12rpx;
  }

  &__info {
    display: flex;
    flex-direction: column;
    gap: 4rpx;
  }

  &__name {
    font-size: 28rpx;
    font-weight: 700;
    color: $cf-white;
  }

  &__venue {
    font-size: 22rpx;
    color: $cf-text-3;
  }

  &__court {
    font-size: 22rpx;
    color: $cf-text-2;
  }

  &__price {
    display: flex;
    align-items: baseline;
    gap: 12rpx;
    margin-bottom: 12rpx;
  }

  &__amount {
    font-size: 40rpx;
    font-weight: 800;
    color: $cf-lime;
  }

  &__original {
    font-size: 24rpx;
    color: $cf-text-3;
    text-decoration: line-through;
  }

  &__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8rpx;
  }

  &__tag {
    font-size: 22rpx;
    color: $cf-text-2;
    background: $cf-glass-bg;
    padding: 4rpx 12rpx;
    border-radius: $r-full;
  }
}
</style>
