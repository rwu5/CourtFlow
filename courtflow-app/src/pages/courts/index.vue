<template>
  <view class="courts">

    <!-- ── Mesh background (matches home/courses) ──────────────────────────── -->
    <view class="courts__mesh" />
    <view class="courts__statusbar" />

    <!-- ── Sticky header ──────────────────────────────────────────────────── -->
    <view class="courts__header">
      <view class="courts__header-top">
        <view class="courts__title-col">
          <text class="courts__title">选场地</text>
          <view class="courts__location-row">
            <cf-icon name="location" :size="16" color="#B8D430" />
            <text class="courts__location-text">朝阳区 · 附近 5km</text>
          </view>
        </view>
        <view class="courts__header-actions">
          <view class="courts__search-btn" @tap="showSearch = !showSearch">
            <cf-icon name="search" :size="20" color="rgba(255,255,255,0.7)" />
          </view>
          <view class="courts__view-toggle" @tap="listView = !listView">
            <view class="courts__toggle-opt" :class="{ 'courts__toggle-opt--active': listView }">
              <view class="courts__toggle-lines">
                <view class="courts__tl" /><view class="courts__tl" /><view class="courts__tl" />
              </view>
            </view>
            <view class="courts__toggle-opt" :class="{ 'courts__toggle-opt--active': !listView }">
              <view class="courts__toggle-grid">
                <view class="courts__tg" /><view class="courts__tg" />
                <view class="courts__tg" /><view class="courts__tg" />
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- Search bar (expandable) -->
      <view class="courts__search-bar" :class="{ 'courts__search-bar--open': showSearch }">
        <cf-icon name="search" :size="18" color="rgba(255,255,255,0.4)" />
        <input
          v-model="searchQuery"
          class="courts__search-input"
          placeholder="搜索场馆名、地址、场地类型…"
          placeholder-class="courts__search-ph"
        />
        <view v-if="searchQuery" @tap="searchQuery = ''" class="courts__search-clear">
          <cf-icon name="close" :size="16" color="rgba(255,255,255,0.4)" />
        </view>
      </view>

      <!-- ── Indoor / Outdoor segmented toggle ───────────────────────────── -->
      <view class="courts__env-row">
        <view class="courts__env-toggle">
          <view
            v-for="e in envOptions"
            :key="e.key"
            class="courts__env-opt"
            :class="[
              { 'courts__env-opt--active': activeEnv === e.key },
              `courts__env-opt--${e.key}`,
            ]"
            @tap="activeEnv = e.key"
          >
            <text class="courts__env-label">{{ e.label }}</text>
          </view>
        </view>

        <!-- Live count pill -->
        <view class="courts__live-pill" v-if="activeSort === 'now'">
          <view class="courts__live-dot" />
          <text class="courts__live-pill-text">{{ liveCount }} 时段可约</text>
        </view>
      </view>

      <!-- Surface filter chips -->
      <scroll-view class="courts__filters-scroll" scroll-x>
        <view class="courts__filters-row">
          <view
            v-for="f in surfaceFilters"
            :key="f.key"
            class="courts__filter-chip"
            :class="{ 'courts__filter-chip--active': activeSurface === f.key }"
            @tap="activeSurface = f.key"
          >
            <text class="courts__filter-text">{{ f.label }}</text>
          </view>
        </view>
      </scroll-view>

      <!-- Sort + date row -->
      <view class="courts__sort-row">
        <view
          v-for="s in sortOptions"
          :key="s.key"
          class="courts__sort-btn"
          :class="{ 'courts__sort-btn--active': activeSort === s.key }"
          @tap="activeSort = s.key"
        >
          <cf-icon :name="s.icon" :size="14"
            :color="activeSort === s.key ? '#B8D430' : 'rgba(255,255,255,0.4)'" />
          <text class="courts__sort-text">{{ s.label }}</text>
        </view>

        <view class="courts__sort-sep" />

        <scroll-view class="courts__date-mini-scroll" scroll-x>
          <view class="courts__date-mini-row">
            <view
              v-for="d in dateTabs"
              :key="d.dateStr"
              class="courts__date-mini-chip"
              :class="{ 'courts__date-mini-chip--active': selectedDate === d.dateStr }"
              @tap="onDateSelect(d.dateStr)"
            >
              <text class="courts__date-mini-text">
                {{ d.isToday ? '今天' : d.weekday + d.day }}
              </text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view><!-- /header -->

    <!-- ── Court list ─────────────────────────────────────────────────────── -->
    <scroll-view class="courts__scroll" scroll-y>

      <!-- Live-now banner -->
      <view class="courts__live-banner" v-if="activeSort === 'now'">
        <view class="courts__live-banner-dot" />
        <text class="courts__live-text">实时更新 · {{ liveCount }} 个时段现在可预订</text>
        <text class="courts__live-time">{{ currentTime }}</text>
      </view>

      <!-- Stats row -->
      <view class="courts__stats-row">
        <text class="courts__stats-text">
          共 <text class="courts__stats-num">{{ filteredCourts.length }}</text> 块场地
          <text class="courts__stats-env" :class="`courts__stats-env--${activeEnv}`">
            · {{ currentEnvLabel }}
          </text>
        </text>
        <view class="courts__stats-right">
          <view class="courts__avail-dot courts__avail-dot--high" />
          <text class="courts__stats-sub">多空位</text>
          <view class="courts__avail-dot courts__avail-dot--low" />
          <text class="courts__stats-sub">少量</text>
          <view class="courts__avail-dot courts__avail-dot--none" />
          <text class="courts__stats-sub">已满</text>
        </view>
      </view>

      <!-- ── Card list ───────────────────────────────────────────────────── -->
      <view class="courts__list" :class="{ 'courts__list--grid': !listView }">
        <view
          v-for="court in filteredCourts"
          :key="court.id"
          class="courts__card"
          :class="{ 'courts__card--grid': !listView }"
          @tap="goCourtDetail(court)"
        >

          <!-- Thumbnail -->
          <view class="courts__card-thumb-wrap">
            <image class="courts__card-thumb" :src="court.photo" mode="aspectFill" />
            <view
              class="courts__card-env-tint"
              :class="court.isIndoor
                ? 'courts__card-env-tint--indoor'
                : 'courts__card-env-tint--outdoor'"
            />
            <view class="courts__card-thumb-overlay" />

            <!-- Availability badge -->
            <view class="courts__card-avail-badge"
              :class="`courts__card-avail-badge--${court.availTier}`">
              <view class="courts__card-avail-dot" />
              <text class="courts__card-avail-text">{{ court.availLabel }}</text>
            </view>

            <!-- Indoor / outdoor badge -->
            <view
              class="courts__card-env-badge"
              :class="court.isIndoor
                ? 'courts__card-env-badge--indoor'
                : 'courts__card-env-badge--outdoor'"
            >
              <text class="courts__card-env-text">
                {{ court.isIndoor ? '室内' : '室外' }}
              </text>
            </view>

            <!-- Surface tag -->
            <view class="courts__card-surface-tag"
              :style="{
                background: court.surfaceColor + '22',
                borderColor: court.surfaceColor + '55',
              }">
              <text class="courts__card-surface-text"
                :style="{ color: court.surfaceColor }">
                {{ court.surface }}
              </text>
            </view>
          </view>

          <!-- Card content -->
          <view class="courts__card-content">

            <!-- Name + distance -->
            <view class="courts__card-top">
              <view class="courts__card-name-col">
                <text class="courts__card-venue">{{ court.venueName }}</text>
                <text class="courts__card-name">{{ court.name }}</text>
              </view>
              <view class="courts__card-dist-col">
                <cf-icon name="location" :size="14" color="rgba(255,255,255,0.35)" />
                <text class="courts__card-dist">{{ court.distance }}</text>
              </view>
            </view>

            <!-- Meta: rating · hours · tags · price -->
            <view class="courts__card-meta">
              <view class="courts__card-rating">
                <cf-icon name="star" :size="13" color="#FBBF24" />
                <text class="courts__card-rating-text">{{ court.rating }}</text>
              </view>
              <view class="courts__card-sep-dot" />
              <text class="courts__card-hours">{{ court.openTime }}–{{ court.closeTime }}</text>
              <view v-if="court.hasLighting" class="courts__card-feature-tag courts__card-feature-tag--amber">
                <text>夜灯</text>
              </view>
              <view class="courts__card-price-tag">
                <text class="courts__card-price">¥{{ court.pricePerHour }}</text>
                <text class="courts__card-price-u">/时</text>
              </view>
            </view>

            <!-- ── Membership strip ────────────────────────────────────── -->
            <view
              v-if="court.memberPrice"
              class="courts__member-strip"
              @tap.stop="joinMembership(court)"
            >
              <view class="courts__member-left">
                <text class="courts__member-label">会员价</text>
                <text class="courts__member-price">¥{{ court.memberPrice }}<text class="courts__member-u">/时</text></text>
              </view>
              <view class="courts__member-cta">
                <text class="courts__member-cta-text">加入</text>
              </view>
            </view>

            <!-- Today's slots -->
            <view class="courts__card-slots">
              <text class="courts__card-slots-label">{{ selectedDateLabel }} 可订</text>
              <view class="courts__card-slots-row">
                <view
                  v-for="slot in court.todaySlots.slice(0, 5)"
                  :key="slot.time"
                  class="courts__slot-chip"
                  :class="{
                    'courts__slot-chip--peak':   slot.isPeak,
                    'courts__slot-chip--avail':  slot.status === 'available',
                    'courts__slot-chip--booked': slot.status === 'booked',
                  }"
                  @tap.stop="quickBook(court, slot)"
                >
                  <text class="courts__slot-chip-time">{{ slot.time }}</text>
                  <text v-if="slot.status === 'available'" class="courts__slot-chip-price">
                    ¥{{ slot.price }}
                  </text>
                  <text v-else class="courts__slot-chip-booked">满</text>
                </view>
                <view v-if="court.todaySlots.length > 5" class="courts__slot-more">
                  <text class="courts__slot-more-text">+{{ court.todaySlots.length - 5 }}</text>
                </view>
              </view>
            </view>

            <!-- Coaches + book CTA -->
            <view class="courts__card-coaches" v-if="court.coaches.length > 0">
              <view class="courts__card-coaches-avatars">
                <image
                  v-for="(av, i) in court.coaches.slice(0, 3)"
                  :key="i"
                  class="courts__card-coach-av"
                  :style="{ left: (i * 22) + 'px', zIndex: 4 - i }"
                  :src="av.avatar"
                  mode="aspectFill"
                />
              </view>
              <text class="courts__card-coaches-text">{{ court.coaches.length }} 位驻场教练</text>
              <view class="courts__card-book-btn"
                :class="{ 'courts__card-book-btn--disabled': court.availTier === 'none' }">
                <text class="courts__card-book-text">
                  {{ court.availTier === 'none' ? '已满' : '预订' }}
                </text>
                <cf-icon v-if="court.availTier !== 'none'"
                  name="chevron-right" :size="14" color="#fff" />
              </view>
            </view>

          </view><!-- /card-content -->
        </view><!-- /card -->
      </view><!-- /list -->

      <!-- Empty state -->
      <view v-if="filteredCourts.length === 0" class="courts__empty">
        <cf-icon name="court" :size="72" color="rgba(255,255,255,0.1)" />
        <text class="courts__empty-title">暂无符合条件的场地</text>
        <text class="courts__empty-sub">试试调整筛选条件</text>
        <view class="courts__empty-btn"
          @tap="activeSurface = 'all'; activeSort = 'distance'; activeEnv = 'all'">
          <text class="courts__empty-btn-text">重置筛选</text>
        </view>
      </view>

      <view style="height: 160rpx;" />
    </scroll-view>

    <cf-tab-bar current="/pages/courts/index" />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfTabBar from '@/components/ui/CfTabBar.vue'

// ── State ─────────────────────────────────────────────────────────────────────
const showSearch    = ref(false)
const searchQuery   = ref('')
const activeSurface = ref('all')
const activeSort    = ref('distance')
const activeEnv     = ref('all')
const listView      = ref(true)
const selectedDate  = ref('')
const currentTime   = ref('')
const liveCount     = ref(23)

const envOptions = [
  { key: 'all',     label: '全部' },
  { key: 'indoor',  label: '🏠 室内' },
  { key: 'outdoor', label: '☀️ 室外' },
]

const surfaceFilters = [
  { key: 'all',  label: '全部场地' },
  { key: '硬地', label: '🏅 硬地' },
  { key: '红土', label: '🟤 红土' },
  { key: '草地', label: '🌿 草地' },
  { key: '合成', label: '⚡ 合成' },
]

const sortOptions = [
  { key: 'distance', icon: 'location', label: '距离优先' },
  { key: 'now',      icon: 'clock',    label: '现在可约' },
  { key: 'price',    icon: 'star',     label: '价格最低' },
]

// ── Date tabs ─────────────────────────────────────────────────────────────────
const dateTabs = computed(() => {
  const days = ['日','一','二','三','四','五','六']
  const now = new Date()
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(now)
    d.setDate(now.getDate() + i)
    return {
      dateStr: d.toISOString().slice(0, 10),
      weekday: '周' + days[d.getDay()],
      day: d.getDate(),
      isToday: i === 0,
    }
  })
})

const selectedDateLabel = computed(() => {
  const d = dateTabs.value.find(d => d.dateStr === selectedDate.value)
  if (!d) return '今天'
  return d.isToday ? '今天' : d.weekday
})

const currentEnvLabel = computed(() => {
  if (activeEnv.value === 'indoor')  return '室内场地'
  if (activeEnv.value === 'outdoor') return '室外场地'
  return '全部'
})

// ── Mock data ─────────────────────────────────────────────────────────────────
function makeSlots(courtId: string, date: string, priceBase: number) {
  const hours = [7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
  return hours.map(h => {
    const time = (h < 10 ? '0' : '') + h + ':00'
    const seed = (courtId + date + time).split('').reduce((a, c) => a + c.charCodeAt(0), 0)
    const r = seed % 10
    const isPeak = h >= 18 || (h >= 8 && h <= 10)
    const price = isPeak ? priceBase + 20 : priceBase
    return { time, status: r < 4 ? 'booked' : 'available', price, isPeak }
  }).filter(s => s.status === 'available').slice(0, 8)
}

const allCourts = ref([
  {
    id: 'v1c1', venueName: '卓越网球中心', name: '硬地1号场',
    surface: '硬地', surfaceColor: '#4299e1',
    isIndoor: false, hasLighting: true,
    photo: '/static/venue-placeholder.jpg',
    distance: '0.8km', rating: 4.9,
    openTime: '07:00', closeTime: '22:00',
    pricePerHour: 80, memberPrice: 64,
    availTier: 'high', availLabel: '多空位',
    venueId: '1', courtId: 'court1',
    coaches: [
      { avatar: '/static/coach-placeholder.jpg' },
      { avatar: '/static/coach-placeholder.jpg' },
    ],
    todaySlots: [] as any[],
  },
  {
    id: 'v1c2', venueName: '卓越网球中心', name: '红土2号场',
    surface: '红土', surfaceColor: '#ed8936',
    isIndoor: false, hasLighting: false,
    photo: '/static/venue-placeholder.jpg',
    distance: '0.8km', rating: 4.8,
    openTime: '07:00', closeTime: '21:00',
    pricePerHour: 120, memberPrice: null,
    availTier: 'low', availLabel: '少量空位',
    venueId: '1', courtId: 'court3',
    coaches: [{ avatar: '/static/coach-placeholder.jpg' }],
    todaySlots: [] as any[],
  },
  {
    id: 'v2c1', venueName: '国贸体育中心', name: '室内硬地A',
    surface: '硬地', surfaceColor: '#4299e1',
    isIndoor: true, hasLighting: true,
    photo: '/static/venue-placeholder.jpg',
    distance: '1.2km', rating: 4.7,
    openTime: '06:00', closeTime: '23:00',
    pricePerHour: 150, memberPrice: 115,
    availTier: 'high', availLabel: '多空位',
    venueId: '2', courtId: 'court1',
    coaches: [
      { avatar: '/static/coach-placeholder.jpg' },
      { avatar: '/static/coach-placeholder.jpg' },
      { avatar: '/static/coach-placeholder.jpg' },
    ],
    todaySlots: [] as any[],
  },
  {
    id: 'v2c2', venueName: '国贸体育中心', name: '硬地3号场',
    surface: '硬地', surfaceColor: '#4299e1',
    isIndoor: false, hasLighting: true,
    photo: '/static/venue-placeholder.jpg',
    distance: '1.2km', rating: 4.6,
    openTime: '07:00', closeTime: '22:00',
    pricePerHour: 90, memberPrice: null,
    availTier: 'none', availLabel: '今日已满',
    venueId: '2', courtId: 'court2',
    coaches: [],
    todaySlots: [] as any[],
  },
  {
    id: 'v3c1', venueName: '朝阳公园球场', name: '露天硬地1',
    surface: '硬地', surfaceColor: '#4299e1',
    isIndoor: false, hasLighting: false,
    photo: '/static/venue-placeholder.jpg',
    distance: '2.1km', rating: 4.5,
    openTime: '08:00', closeTime: '20:00',
    pricePerHour: 60, memberPrice: 48,
    availTier: 'high', availLabel: '多空位',
    venueId: '3', courtId: 'court1',
    coaches: [{ avatar: '/static/coach-placeholder.jpg' }],
    todaySlots: [] as any[],
  },
  {
    id: 'v3c2', venueName: '朝阳公园球场', name: '红土精品场',
    surface: '红土', surfaceColor: '#ed8936',
    isIndoor: false, hasLighting: false,
    photo: '/static/venue-placeholder.jpg',
    distance: '2.1km', rating: 4.7,
    openTime: '08:00', closeTime: '20:00',
    pricePerHour: 100, memberPrice: null,
    availTier: 'low', availLabel: '少量空位',
    venueId: '3', courtId: 'court4',
    coaches: [],
    todaySlots: [] as any[],
  },
  {
    id: 'v4c1', venueName: '中信天津俱乐部', name: '草地A场',
    surface: '草地', surfaceColor: '#48bb78',
    isIndoor: false, hasLighting: true,
    photo: '/static/venue-placeholder.jpg',
    distance: '3.4km', rating: 4.9,
    openTime: '07:00', closeTime: '22:00',
    pricePerHour: 200, memberPrice: 160,
    availTier: 'low', availLabel: '少量空位',
    venueId: '4', courtId: 'court1',
    coaches: [
      { avatar: '/static/coach-placeholder.jpg' },
      { avatar: '/static/coach-placeholder.jpg' },
    ],
    todaySlots: [] as any[],
  },
])

// ── Computed ──────────────────────────────────────────────────────────────────
const filteredCourts = computed(() => {
  let list = allCourts.value

  if (activeEnv.value === 'indoor')  list = list.filter(c => c.isIndoor)
  if (activeEnv.value === 'outdoor') list = list.filter(c => !c.isIndoor)

  if (activeSurface.value !== 'all') {
    list = list.filter(c => c.surface === activeSurface.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(c =>
      c.venueName.toLowerCase().includes(q) ||
      c.name.toLowerCase().includes(q) ||
      c.surface.toLowerCase().includes(q)
    )
  }
  if (activeSort.value === 'price') {
    list = [...list].sort((a, b) => a.pricePerHour - b.pricePerHour)
  } else if (activeSort.value === 'now') {
    list = [...list].filter(c => c.availTier !== 'none')
  }
  return list
})

// ── Actions ───────────────────────────────────────────────────────────────────
function onDateSelect(dateStr: string) {
  selectedDate.value = dateStr
  allCourts.value.forEach(c => {
    c.todaySlots = makeSlots(c.id, dateStr, c.pricePerHour)
  })
}

function updateTime() {
  const now = new Date()
  currentTime.value = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0')
}

function goCourtDetail(court: any) {
  uni.navigateTo({
    url: `/packages/venue/detail/index?venueId=${court.venueId}&courtId=${court.courtId}`,
  })
}

function quickBook(court: any, slot: any) {
  uni.navigateTo({
    url: `/packages/venue/detail/index?venueId=${court.venueId}&courtId=${court.courtId}&date=${selectedDate.value}&slot=${slot.time}`,
  })
}

function joinMembership(court: any) {
  uni.navigateTo({
    url: `/packages/membership/join/index?venueId=${court.venueId}`,
  })
}

onMounted(() => {
  selectedDate.value = dateTabs.value[0].dateStr
  updateTime()
  setInterval(updateTime, 60000)
  allCourts.value.forEach(c => {
    c.todaySlots = makeSlots(c.id, selectedDate.value, c.pricePerHour)
  })
})
</script>

<style lang="scss">
@import '@/uni.scss';

// ── Root ──────────────────────────────────────────────────────────────────────
.courts {
  background: $cf-bg;
  min-height: 100vh;
  position: relative;
}

// ── Mesh — matches home page exactly ─────────────────────────────────────────
.courts__mesh {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 700rpx;
  background:
    radial-gradient(ellipse at 15% 5%,  rgba(45,139,87,0.22)  0%, transparent 55%),
    radial-gradient(ellipse at 85% 5%,  rgba(46,134,193,0.18) 0%, transparent 50%),
    radial-gradient(ellipse at 55% 85%, rgba(184,212,48,0.08) 0%, transparent 45%),
    radial-gradient(ellipse at 92% 60%, rgba(123,79,160,0.07) 0%, transparent 40%);
  pointer-events: none;
  z-index: 0;
  animation: meshBreathe 6s ease-in-out infinite;
}

.courts__statusbar {
  height: var(--status-bar-height, 44px);
  background: transparent;
}

// ── Header ────────────────────────────────────────────────────────────────────
.courts__header {
  position: sticky;
  top: 0;
  z-index: 20;
  background: rgba(8,14,11,0.88);
  backdrop-filter: blur(20px) saturate(1.3);
  -webkit-backdrop-filter: blur(20px) saturate(1.3);
  border-bottom: 0.5px solid $cf-line;
  padding-bottom: 12rpx;
}

.courts__header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 32rpx 12rpx;
}

.courts__title {
  font-size: 44rpx;
  font-weight: 900;
  color: $cf-white;
  letter-spacing: -0.02em;
  display: block;
  background: linear-gradient(90deg, #fff 0%, rgba(184,212,48,0.85) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.courts__location-row {
  display: flex; align-items: center; gap: 5rpx; margin-top: 4rpx;
}
.courts__location-text { font-size: 20rpx; color: $cf-text-2; }

.courts__header-actions { display: flex; align-items: center; gap: 12rpx; }

.courts__search-btn {
  width: 64rpx; height: 64rpx;
  background: $cf-glass-bg;
  border-radius: $r-full;
  border: 0.5px solid $cf-glass-border;
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(8px);
  &:active { opacity: 0.75; }
}

.courts__view-toggle {
  display: flex;
  background: $cf-glass-bg;
  border-radius: $r-full;
  border: 0.5px solid $cf-glass-border;
  overflow: hidden;
  padding: 4rpx;
  gap: 2rpx;
}
.courts__toggle-opt {
  width: 52rpx; height: 52rpx;
  border-radius: 9999rpx;
  display: flex; align-items: center; justify-content: center;
  &--active { background: rgba(184,212,48,0.15); }
}
.courts__toggle-lines { display: flex; flex-direction: column; gap: 4rpx; }
.courts__tl {
  width: 20rpx; height: 2rpx;
  background: rgba(255,255,255,0.4); border-radius: 1rpx;
  .courts__toggle-opt--active & { background: $cf-lime; }
}
.courts__toggle-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4rpx; }
.courts__tg {
  width: 8rpx; height: 8rpx;
  background: rgba(255,255,255,0.4); border-radius: 2rpx;
  .courts__toggle-opt--active & { background: $cf-lime; }
}

// Search bar
.courts__search-bar {
  display: flex; align-items: center; gap: 12rpx;
  margin: 0 24rpx;
  background: $cf-glass-bg;
  border-radius: $r-lg;
  border: 0.5px solid $cf-glass-border;
  padding: 0 20rpx;
  height: 0; overflow: hidden; opacity: 0;
  transition: height 0.25s ease, opacity 0.2s ease, margin 0.25s ease;
  &--open { height: 80rpx; opacity: 1; margin-bottom: 12rpx; }
}
.courts__search-input { flex: 1; font-size: 26rpx; color: $cf-white; background: transparent; }
.courts__search-ph   { color: rgba(255,255,255,0.22); }
.courts__search-clear { padding: 8rpx; &:active { opacity: 0.6; } }

// ── Indoor / Outdoor toggle ────────────────────────────────────────────────────
.courts__env-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4rpx 24rpx 10rpx;
  gap: 12rpx;
}
.courts__env-toggle {
  display: flex;
  background: rgba(255,255,255,0.05);
  border-radius: $r-full;
  border: 0.5px solid $cf-line;
  padding: 4rpx;
  gap: 2rpx;
}
.courts__env-opt {
  padding: 9rpx 24rpx;
  border-radius: $r-full;
  transition: background 0.2s;
  &:active { opacity: 0.75; }

  // default state — neutral
  &--active { background: rgba(255,255,255,0.09); }

  // indoor active — blue tint
  &--indoor#{&}--active {
    background: rgba(46,134,193,0.18);
  }
  // outdoor active — green tint
  &--outdoor#{&}--active {
    background: rgba(45,139,87,0.18);
  }
}
.courts__env-label {
  font-size: 22rpx; font-weight: 600;
  color: $cf-text-2;
  .courts__env-opt--active & { color: $cf-white; font-weight: 700; }
  .courts__env-opt--indoor.courts__env-opt--active & { color: #63b3ed; }
  .courts__env-opt--outdoor.courts__env-opt--active & { color: $cf-success; }
}

// Live pill (re-used from home hero badge style)
.courts__live-pill {
  display: flex; align-items: center; gap: 7rpx;
  background: rgba(52,211,153,0.08);
  border: 0.5px solid rgba(52,211,153,0.22);
  border-radius: $r-full;
  padding: 8rpx 18rpx;
  flex-shrink: 0;
}
.courts__live-dot {
  width: 8rpx; height: 8rpx; border-radius: $r-full;
  background: $cf-success;
  box-shadow: 0 0 6rpx rgba(52,211,153,0.8);
  animation: pulse 2s infinite;
  flex-shrink: 0;
}
.courts__live-pill-text { font-size: 19rpx; color: $cf-success; font-weight: 600; }

// Surface filter chips
.courts__filters-scroll { padding: 0 24rpx; }
.courts__filters-row { display: flex; gap: 10rpx; padding: 4rpx 0 10rpx; }
.courts__filter-chip {
  flex-shrink: 0;
  padding: 10rpx 22rpx;
  border-radius: $r-full;
  background: rgba(255,255,255,0.05);
  border: 0.5px solid $cf-line;
  &--active {
    background: rgba(184,212,48,0.11);
    border-color: rgba(184,212,48,0.38);
  }
  &:active { opacity: 0.75; }
}
.courts__filter-text {
  font-size: 24rpx; font-weight: 500; color: $cf-text-2;
  .courts__filter-chip--active & { color: $cf-lime; font-weight: 700; }
}

// Sort row
.courts__sort-row {
  display: flex; align-items: center; gap: 6rpx;
  padding: 0 24rpx 8rpx;
}
.courts__sort-btn {
  display: flex; align-items: center; gap: 5rpx;
  padding: 8rpx 14rpx;
  border-radius: $r-full;
  border: 0.5px solid transparent;
  flex-shrink: 0;
  &--active {
    background: rgba(184,212,48,0.09);
    border-color: rgba(184,212,48,0.25);
  }
  &:active { opacity: 0.75; }
}
.courts__sort-text {
  font-size: 20rpx; color: $cf-text-2;
  .courts__sort-btn--active & { color: $cf-lime; font-weight: 600; }
}
.courts__sort-sep {
  width: 1rpx; height: 28rpx; background: $cf-line; margin: 0 2rpx; flex-shrink: 0;
}

// Date mini chips (matches home page date chip style)
.courts__date-mini-scroll { flex: 1; }
.courts__date-mini-row { display: flex; gap: 8rpx; }
.courts__date-mini-chip {
  flex-shrink: 0;
  padding: 7rpx 16rpx;
  border-radius: $r-full;
  background: rgba(255,255,255,0.04);
  border: 0.5px solid $cf-line;
  &--active {
    background: rgba(45,139,87,0.16);
    border-color: rgba(45,139,87,0.38);
  }
  &:active { opacity: 0.75; }
}
.courts__date-mini-text {
  font-size: 20rpx; color: $cf-text-2;
  .courts__date-mini-chip--active & { color: $cf-success; font-weight: 700; }
}

// ── Live banner ───────────────────────────────────────────────────────────────
.courts__live-banner {
  display: flex; align-items: center; gap: 10rpx;
  margin: 16rpx 28rpx 0;
  background: rgba(52,211,153,0.07);
  border-radius: $r-lg;
  border: 0.5px solid rgba(52,211,153,0.18);
  padding: 14rpx 20rpx;
}
.courts__live-banner-dot {
  width: 12rpx; height: 12rpx; border-radius: $r-full;
  background: $cf-success;
  box-shadow: 0 0 8rpx rgba(52,211,153,0.7);
  animation: pulse 2s infinite;
  flex-shrink: 0;
}
.courts__live-text { font-size: 22rpx; color: $cf-success; flex: 1; font-weight: 500; }
.courts__live-time { font-size: 20rpx; color: $cf-text-2; flex-shrink: 0; }

// ── Stats row ─────────────────────────────────────────────────────────────────
.courts__stats-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16rpx 32rpx 8rpx;
}
.courts__stats-text { font-size: 22rpx; color: $cf-text-2; }
.courts__stats-num  { color: $cf-white; font-weight: 700; }
.courts__stats-env  {
  &--indoor  { color: #63b3ed; }
  &--outdoor { color: $cf-success; }
  &--all     { color: $cf-text-2; }
}
.courts__stats-right { display: flex; align-items: center; gap: 8rpx; }
.courts__stats-sub  { font-size: 18rpx; color: $cf-text-3; }
.courts__avail-dot {
  width: 10rpx; height: 10rpx; border-radius: $r-full;
  &--high { background: $cf-success; }
  &--low  { background: $cf-amber; }
  &--none { background: rgba(255,255,255,0.2); }
}

// ── List / Grid ───────────────────────────────────────────────────────────────
.courts__list {
  padding: 0 28rpx;
  display: flex; flex-direction: column; gap: 16rpx;
  &--grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14rpx;
  }
}
.courts__scroll { flex: 1; }

// ── Court card (horizontal list style) ───────────────────────────────────────
.courts__card {
  display: flex;
  background: $cf-glass-bg;
  border-radius: $r-xl;
  border: 0.5px solid $cf-glass-border;
  overflow: hidden;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 4rpx 24rpx rgba(0,0,0,0.18);
  transition: border-color 0.2s, box-shadow 0.2s;
  &:active { opacity: 0.88; }
  &--grid { flex-direction: column; }
}

// Thumbnail
.courts__card-thumb-wrap {
  position: relative;
  width: 200rpx;
  flex-shrink: 0;
  .courts__card--grid & { width: 100%; height: 180rpx; }
}
.courts__card-thumb { width: 100%; height: 100%; background: $cf-card-solid; }

// Subtle environment colour tint on the photo
.courts__card-env-tint {
  position: absolute; inset: 0;
  pointer-events: none;
  &--indoor  {
    background: linear-gradient(
      135deg,
      rgba(46,134,193,0.22) 0%,
      transparent 70%
    );
  }
  &--outdoor {
    background: linear-gradient(
      135deg,
      rgba(45,139,87,0.20) 0%,
      transparent 70%
    );
  }
}

.courts__card-thumb-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to right, transparent 40%, rgba(8,14,11,0.3) 100%);
  .courts__card--grid & {
    background: linear-gradient(to bottom, transparent 40%, rgba(8,14,11,0.75) 100%);
  }
}

// Availability badge
.courts__card-avail-badge {
  position: absolute; top: 10rpx; left: 10rpx;
  display: flex; align-items: center; gap: 5rpx;
  padding: 4rpx 10rpx; border-radius: $r-full;
  backdrop-filter: blur(8px);
  &--high { background: rgba(52,211,153,0.18); border: 0.5px solid rgba(52,211,153,0.35); }
  &--low  { background: rgba(251,191,36,0.18); border: 0.5px solid rgba(251,191,36,0.35); }
  &--none { background: rgba(240,69,69,0.15);  border: 0.5px solid rgba(240,69,69,0.3); }
}
.courts__card-avail-dot {
  width: 7rpx; height: 7rpx; border-radius: $r-full;
  .courts__card-avail-badge--high & { background: $cf-success; }
  .courts__card-avail-badge--low  & { background: $cf-amber; }
  .courts__card-avail-badge--none & { background: $cf-danger; }
}
.courts__card-avail-text {
  font-size: 16rpx; font-weight: 700;
  .courts__card-avail-badge--high & { color: $cf-success; }
  .courts__card-avail-badge--low  & { color: $cf-amber; }
  .courts__card-avail-badge--none & { color: $cf-danger; }
}

// Indoor / outdoor badge — bottom of thumb
.courts__card-env-badge {
  position: absolute; bottom: 10rpx; left: 10rpx;
  padding: 3rpx 10rpx; border-radius: $r-full;
  backdrop-filter: blur(6px);
  &--indoor  {
    background: rgba(46,134,193,0.22);
    border: 0.5px solid rgba(46,134,193,0.5);
  }
  &--outdoor {
    background: rgba(45,139,87,0.22);
    border: 0.5px solid rgba(45,139,87,0.45);
  }
}
.courts__card-env-text {
  font-size: 16rpx; font-weight: 700;
  .courts__card-env-badge--indoor  & { color: #63b3ed; }
  .courts__card-env-badge--outdoor & { color: $cf-success; }
}

// Surface tag
.courts__card-surface-tag {
  position: absolute; bottom: 10rpx; right: 8rpx;
  padding: 3rpx 9rpx; border-radius: $r-full;
  border: 0.5px solid;
  backdrop-filter: blur(6px);
}
.courts__card-surface-text { font-size: 16rpx; font-weight: 700; }

// ── Card content ──────────────────────────────────────────────────────────────
.courts__card-content {
  flex: 1;
  padding: 16rpx 18rpx;
  display: flex; flex-direction: column; gap: 9rpx;
  min-width: 0;
}

.courts__card-top {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 8rpx;
}
.courts__card-name-col { flex: 1; min-width: 0; }
.courts__card-venue {
  font-size: 18rpx; color: $cf-text-2;
  display: block; margin-bottom: 2rpx;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.courts__card-name {
  font-size: 27rpx; font-weight: 800; color: $cf-white;
  display: block; letter-spacing: -0.01em;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.courts__card-dist-col { display: flex; align-items: center; gap: 3rpx; flex-shrink: 0; }
.courts__card-dist { font-size: 18rpx; color: $cf-text-3; }

.courts__card-meta {
  display: flex; align-items: center; gap: 7rpx; flex-wrap: wrap;
}
.courts__card-rating { display: flex; align-items: center; gap: 3rpx; }
.courts__card-rating-text { font-size: 19rpx; font-weight: 700; color: $cf-amber; }
.courts__card-sep-dot {
  width: 3rpx; height: 3rpx; border-radius: $r-full; background: $cf-text-3;
}
.courts__card-hours { font-size: 18rpx; color: $cf-text-3; }
.courts__card-feature-tag {
  padding: 2rpx 9rpx; border-radius: $r-full;
  font-size: 16rpx;
  &--amber {
    background: rgba(251,191,36,0.10);
    border: 0.5px solid rgba(251,191,36,0.25);
    color: $cf-amber;
  }
}
.courts__card-price-tag {
  margin-left: auto; display: flex; align-items: baseline; gap: 1rpx;
}
.courts__card-price { font-size: 26rpx; font-weight: 900; color: $cf-lime; }
.courts__card-price-u { font-size: 16rpx; color: $cf-text-2; }

// ── Membership strip (compact, matches home hero badge aesthetic) ─────────────
.courts__member-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9rpx 14rpx;
  border-radius: $r-md;
  background: linear-gradient(90deg,
    rgba(184,212,48,0.09) 0%,
    rgba(45,139,87,0.07) 100%
  );
  border: 0.5px solid rgba(184,212,48,0.22);
  &:active { opacity: 0.8; }
}
.courts__member-left {
  display: flex; align-items: center; gap: 8rpx;
}
.courts__member-label {
  font-size: 17rpx; color: rgba(184,212,48,0.65); font-weight: 600;
}
.courts__member-price {
  font-size: 22rpx; font-weight: 900; color: $cf-lime;
}
.courts__member-u { font-size: 14rpx; font-weight: 400; color: rgba(184,212,48,0.55); }
.courts__member-cta {
  background: rgba(184,212,48,0.13);
  border: 0.5px solid rgba(184,212,48,0.32);
  border-radius: $r-full;
  padding: 5rpx 16rpx;
}
.courts__member-cta-text { font-size: 19rpx; font-weight: 700; color: $cf-lime; }

// ── Slot chips ────────────────────────────────────────────────────────────────
.courts__card-slots {}
.courts__card-slots-label {
  font-size: 17rpx; color: $cf-text-3; display: block; margin-bottom: 7rpx;
}
.courts__card-slots-row {
  display: flex; flex-wrap: wrap; gap: 6rpx; align-items: center;
}
.courts__slot-chip {
  display: flex; flex-direction: column; align-items: center;
  padding: 6rpx 11rpx;
  border-radius: $r-sm;
  border: 0.5px solid;
  min-width: 64rpx;
  transition: all 0.15s;
  &:active { transform: scale(0.93); }
  &--avail {
    background: rgba(45,139,87,0.09);
    border-color: rgba(45,139,87,0.28);
  }
  &--avail#{&}--peak {
    background: rgba(251,191,36,0.09);
    border-color: rgba(251,191,36,0.28);
  }
  &--booked {
    background: rgba(255,255,255,0.03);
    border-color: rgba(255,255,255,0.06);
    opacity: 0.45;
  }
}
.courts__slot-chip-time {
  font-size: 17rpx; font-weight: 700; color: $cf-white;
  .courts__slot-chip--booked & { color: $cf-text-3; }
  .courts__slot-chip--peak   & { color: $cf-amber; }
}
.courts__slot-chip-price {
  font-size: 14rpx; font-weight: 600; color: $cf-success;
  .courts__slot-chip--peak & { color: $cf-amber; }
}
.courts__slot-chip-booked { font-size: 14rpx; color: $cf-text-3; }
.courts__slot-more {
  width: 42rpx; height: 42rpx;
  background: rgba(255,255,255,0.05);
  border-radius: $r-full;
  display: flex; align-items: center; justify-content: center;
  border: 0.5px solid $cf-line;
}
.courts__slot-more-text { font-size: 16rpx; color: $cf-text-2; }

// ── Coaches row ───────────────────────────────────────────────────────────────
.courts__card-coaches {
  display: flex; align-items: center; gap: 10rpx;
  padding-top: 6rpx;
  border-top: 0.5px solid $cf-line;
}
.courts__card-coaches-avatars {
  position: relative; height: 38rpx; width: 68rpx; flex-shrink: 0;
}
.courts__card-coach-av {
  position: absolute;
  width: 36rpx; height: 36rpx;
  border-radius: $r-full;
  border: 1.5rpx solid $cf-bg;
  background: $cf-card-solid;
}
.courts__card-coaches-text { flex: 1; font-size: 18rpx; color: $cf-text-2; }

.courts__card-book-btn {
  display: flex; align-items: center; gap: 3rpx;
  background: linear-gradient(135deg, $cf-green, $cf-blue);
  border-radius: $r-full;
  padding: 9rpx 18rpx;
  flex-shrink: 0;
  box-shadow: 0 3rpx 12rpx rgba(45,139,87,0.3);
  &:active { opacity: 0.85; }
  &--disabled {
    background: rgba(255,255,255,0.07);
    border: 0.5px solid $cf-line;
    box-shadow: none;
  }
}
.courts__card-book-text {
  font-size: 21rpx; font-weight: 700; color: #fff;
  .courts__card-book-btn--disabled & { color: $cf-text-3; }
}

// ── Empty state ───────────────────────────────────────────────────────────────
.courts__empty {
  display: flex; flex-direction: column; align-items: center;
  padding: 80rpx 48rpx; gap: 16rpx;
}
.courts__empty-title { font-size: 30rpx; font-weight: 600; color: $cf-text-2; }
.courts__empty-sub   { font-size: 24rpx; color: $cf-text-3; }
.courts__empty-btn {
  margin-top: 16rpx;
  padding: 18rpx 48rpx;
  border-radius: $r-full;
  border: 1rpx solid rgba(184,212,48,0.3);
  background: rgba(184,212,48,0.07);
  &:active { opacity: 0.75; }
}
.courts__empty-btn-text { font-size: 26rpx; font-weight: 600; color: $cf-lime; }
</style>
