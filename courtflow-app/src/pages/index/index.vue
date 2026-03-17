<template>
  <view class="home">
    <!-- Mesh gradient background -->
    <view class="home__mesh" />

    <view class="home__statusbar" />

    <!-- Header -->
    <view class="home__header">
      <view class="home__header-left">
        <text class="home__logo">RallyAI</text>
        <text class="home__tagline">智能网球预订平台</text>
      </view>
      <view class="home__header-right">
        <view class="home__notif-btn" @tap="goNotifications">
          <cf-icon name="bell" :size="44" color="rgba(255,255,255,0.8)" />
          <view v-if="hasNotification" class="home__notif-dot" />
        </view>
        <image class="home__avatar" :src="userAvatar" mode="aspectFill" @tap="goProfile" />
      </view>
    </view>

    <scroll-view class="home__scroll" scroll-y>
      <!-- Hero stats card -->
      <view class="home__hero">
        <view class="home__hero-grad" />
        <view class="home__hero-body">
          <view class="home__hero-top">
            <view>
              <text class="home__hero-greeting">{{ greeting }}，{{ userName }}</text>
              <text class="home__hero-sub">{{ currentDateLabel }}</text>
            </view>
            <view class="home__hero-badge">
              <view class="home__hero-badge-dot" />
              <text class="home__hero-badge-text">{{ todayAvailableCount }} 个时段可预订</text>
            </view>
          </view>
          <view class="home__hero-divider" />
          <view class="home__hero-stats">
            <view class="home__hero-stat" @tap="goVenueList">
              <text class="home__hero-stat-val">{{ nearbyVenues.length }}</text>
              <text class="home__hero-stat-label">附近场馆</text>
            </view>
            <view class="home__hero-stat-sep" />
            <view class="home__hero-stat" @tap="goCoaches">
              <text class="home__hero-stat-val">{{ coachCount }}</text>
              <text class="home__hero-stat-label">驻场教练</text>
            </view>
            <view class="home__hero-stat-sep" />
            <view class="home__hero-stat" @tap="goMyOrders">
              <text class="home__hero-stat-val">{{ bookingCount }}</text>
              <text class="home__hero-stat-label">我的预约</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Date quick picker -->
      <view class="home__section">
        <text class="home__section-title">选择日期</text>
        <scroll-view class="home__date-scroll" scroll-x>
          <view class="home__date-row">
            <view
              v-for="d in quickDates"
              :key="d.dateStr"
              class="home__date-chip"
              :class="{ 'home__date-chip--active': selectedQuickDate === d.dateStr }"
              @tap="selectQuickDate(d.dateStr)"
            >
              <text class="home__date-wd">{{ d.weekday }}</text>
              <text class="home__date-day">{{ d.day }}</text>
              <view v-if="d.isToday" class="home__date-today-dot" />
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- Nearby venues -->
      <view class="home__section">
        <view class="home__section-row">
          <text class="home__section-title">附近场馆</text>
          <text class="home__section-more" @tap="goVenueList">全部 →</text>
        </view>
        <scroll-view class="home__hscroll" scroll-x>
          <view class="home__hrow">
            <view
              v-for="v in nearbyVenues"
              :key="v.id"
              class="home__venue-card"
              @tap="goVenueDetail(v.id)"
            >
              <view class="home__venue-img-wrap">
                <image class="home__venue-img" :src="v.coverUrl" mode="aspectFill" />
                <view class="home__venue-img-overlay" />
                <view class="home__venue-self-tag" v-if="v.isSelfOperated">
                  <text class="home__venue-self-text">自营</text>
                </view>
                <view class="home__venue-avail" :class="v.hasAvailability ? '' : 'home__venue-avail--none'">
                  <view class="home__venue-avail-dot" />
                  <text class="home__venue-avail-text">{{ v.hasAvailability ? '有空位' : '已满' }}</text>
                </view>
              </view>
              <view class="home__venue-info">
                <text class="home__venue-name">{{ v.name }}</text>
                <text class="home__venue-meta">{{ v.district }} · {{ v.distanceText }}</text>
                <text class="home__venue-price">¥{{ v.priceFrom }}<text class="home__venue-price-u">起/时</text></text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- Featured Coaches -->
      <view class="home__section">
        <view class="home__section-row">
          <text class="home__section-title">精选教练</text>
          <text class="home__section-more" @tap="goCoaches">全部 →</text>
        </view>
        <scroll-view class="home__hscroll" scroll-x>
          <view class="home__hrow">
            <view
              v-for="c in featuredCoaches"
              :key="c.id"
              class="home__coach-card"
              @tap="goCoachProfile(c.id)"
            >
              <image class="home__coach-avatar" :src="c.avatar" mode="aspectFill" />
              <view class="home__coach-level-ring" :style="{ borderColor: c.color }" />
              <text class="home__coach-name">{{ c.name }}</text>
              <view class="home__coach-cert">
                <text class="home__coach-cert-text">{{ c.cert }}</text>
              </view>
              <text class="home__coach-venue-name">{{ c.venueName }}</text>
              <text class="home__coach-price">¥{{ c.pricePerHour }}/时</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- Upcoming bookings -->
      <view class="home__section">
        <view class="home__section-row">
          <text class="home__section-title">即将到来</text>
          <text class="home__section-more" @tap="goMyOrders">全部 →</text>
        </view>

        <view v-if="upcomingBookings.length > 0">
          <view
            v-for="b in upcomingBookings"
            :key="b.id"
            class="home__booking-card"
            @tap="goOrderDetail(b.id)"
          >
            <view class="home__booking-date">
              <text class="home__booking-month">{{ b.month }}</text>
              <text class="home__booking-day">{{ b.day }}</text>
            </view>
            <view class="home__booking-info">
              <text class="home__booking-venue">{{ b.venueName }}</text>
              <text class="home__booking-detail">{{ b.courtName }} · {{ b.timeRange }}</text>
              <view v-if="b.coachName" class="home__booking-coach-row">
                <cf-icon name="person" :size="28" color="#B8D430" />
                <text class="home__booking-coach">{{ b.coachName }} 教练</text>
              </view>
            </view>
            <view class="home__booking-status-col">
              <view class="home__booking-dot" />
              <text class="home__booking-status">已确认</text>
            </view>
          </view>
        </view>

        <view v-else class="home__empty-card">
          <cf-icon name="ball" :size="80" color="rgba(255,255,255,0.2)" />
          <text class="home__empty-text">暂无即将到来的预约</text>
          <view class="home__empty-btn" @tap="goVenueList">
            <text class="home__empty-btn-text">立即预订</text>
          </view>
        </view>
      </view>

      <view style="height: 160rpx;" />
    </scroll-view>

    <!-- Custom Tab Bar -->
    <cf-tab-bar current="/pages/index/index" />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfTabBar from '@/components/ui/CfTabBar.vue'

const hasNotification = ref(false)
const todayAvailableCount = ref(48)
const selectedQuickDate = ref('')
const coachCount = ref(12)
const bookingCount = ref(3)
const userName = ref('球友')
const userAvatar = ref('/static/default-avatar.png')

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return '早上好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const currentDateLabel = computed(() => {
  const now = new Date()
  const m = now.getMonth() + 1
  const d = now.getDate()
  const wds = ['周日','周一','周二','周三','周四','周五','周六']
  return `${m}月${d}日 ${wds[now.getDay()]}`
})

const quickDates = computed(() => {
  const wds = ['日','一','二','三','四','五','六']
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() + i)
    const pad = (n: number) => String(n).padStart(2,'0')
    return {
      dateStr: `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`,
      weekday: i === 0 ? '今' : `周${wds[d.getDay()]}`,
      day: d.getDate(),
      isToday: i === 0,
    }
  })
})

const nearbyVenues = ref([
  { id:'1', name:'卓越网球中心', district:'朝阳', distanceText:'1.2km',
    coverUrl:'/static/venue-placeholder.jpg', priceFrom:80, isSelfOperated:true, hasAvailability:true },
  { id:'2', name:'国贸球场', district:'东城', distanceText:'2.5km',
    coverUrl:'/static/venue-placeholder.jpg', priceFrom:120, isSelfOperated:false, hasAvailability:true },
  { id:'3', name:'望京体育公园', district:'朝阳', distanceText:'3.1km',
    coverUrl:'/static/venue-placeholder.jpg', priceFrom:60, isSelfOperated:true, hasAvailability:false },
])

const featuredCoaches = ref([
  { id:'c1', name:'张明', cert:'ITF L2', avatar:'/static/coach-placeholder.jpg',
    venueName:'卓越网球中心', pricePerHour:300, color:'#2D8B57' },
  { id:'c2', name:'李华', cert:'LTA L3', avatar:'/static/coach-placeholder.jpg',
    venueName:'国贸球场', pricePerHour:400, color:'#2E86C1' },
  { id:'c3', name:'王芳', cert:'ITF L1', avatar:'/static/coach-placeholder.jpg',
    venueName:'望京体育公园', pricePerHour:250, color:'#7B4FA0' },
])

const upcomingBookings = ref<any[]>([])

onMounted(() => {
  selectedQuickDate.value = quickDates.value[0]?.dateStr ?? ''
})

function selectQuickDate(d: string) { selectedQuickDate.value = d }
function goVenueList() { uni.navigateTo({ url: '/packages/venue/list/index' }) }
function goVenueDetail(id: string) { uni.navigateTo({ url: `/packages/venue/detail/index?id=${id}` }) }
function goCoaches() { uni.switchTab({ url: '/pages/courses/index' }) }
function goCoachProfile(id: string) { uni.navigateTo({ url: `/packages/coach/profile/index?id=${id}` }) }
function goMyOrders() { uni.navigateTo({ url: '/packages/account/orders/index' }) }
function goOrderDetail(id: string) { uni.navigateTo({ url: `/packages/booking/result/index?orderId=${id}&success=1` }) }
function goProfile() { uni.switchTab({ url: '/pages/my/index' }) }
function goNotifications() {}
</script>

<style lang="scss">
@import '@/uni.scss';

.home {
  background: $cf-bg;
  min-height: 100vh;
  position: relative;
}

// ─── Mesh gradient background ─────────────────────────────────────────────────
.home__mesh {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 700rpx;
  background:
    radial-gradient(ellipse at 15% 15%, rgba(45,139,87,0.28) 0%, transparent 55%),
    radial-gradient(ellipse at 85% 5%,  rgba(46,134,193,0.22) 0%, transparent 50%),
    radial-gradient(ellipse at 55% 85%, rgba(184,212,48,0.10) 0%, transparent 45%),
    radial-gradient(ellipse at 92% 60%, rgba(123,79,160,0.09) 0%, transparent 40%);
  pointer-events: none;
  z-index: 0;
  animation: meshBreathe 6s ease-in-out infinite;
}

.home__statusbar { height: var(--status-bar-height, 44px); position: relative; z-index: 2; }

// ─── Header ──────────────────────────────────────────────────────────────────
.home__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12rpx 40rpx 20rpx;
  position: relative;
  z-index: 2;
}

.home__logo {
  display: block;
  font-size: 40rpx;
  font-weight: 900;
  background: linear-gradient(90deg, #4ade80 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}

.home__tagline {
  font-size: 20rpx;
  color: $cf-text-3;
  letter-spacing: 0.06em;
}

.home__header-right { display: flex; align-items: center; gap: 16rpx; }

.home__notif-btn {
  position: relative;
  width: 72rpx; height: 72rpx;
  background: $cf-glass-bg;
  border-radius: $r-full;
  display: flex; align-items: center; justify-content: center;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(12px);
}
.home__notif-icon { font-size: 30rpx; }
.home__notif-dot {
  position: absolute; top: 12rpx; right: 12rpx;
  width: 14rpx; height: 14rpx;
  background: $cf-danger; border-radius: $r-full;
  border: 2rpx solid $cf-bg;
}

.home__avatar {
  width: 72rpx; height: 72rpx;
  border-radius: $r-full;
  border: 2rpx solid $cf-green;
  background: $cf-card-solid;
}

// ─── Scroll ──────────────────────────────────────────────────────────────────
.home__scroll { position: relative; z-index: 1; }

// ─── Hero card ───────────────────────────────────────────────────────────────
.home__hero {
  margin: 0 32rpx 40rpx;
  border-radius: $r-xl;
  overflow: hidden;
  position: relative;
  border: 0.5px solid $cf-glass-border-2;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  background: $cf-glass-bg;
  box-shadow: 0 8rpx 40rpx rgba(0,0,0,0.25), 0 0 1px $cf-glass-border;
}

.home__hero-grad {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(45,139,87,0.18) 0%, rgba(46,134,193,0.14) 100%);
  pointer-events: none;
}

.home__hero-body { position: relative; padding: 32rpx; }

.home__hero-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.home__hero-greeting {
  display: block;
  font-size: 34rpx;
  font-weight: 800;
  color: $cf-white;
  letter-spacing: -0.01em;
}

.home__hero-sub {
  font-size: 20rpx;
  color: $cf-text-2;
  margin-top: 4rpx;
  display: block;
}

.home__hero-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: rgba(184,212,48,0.12);
  border: 0.5px solid rgba(184,212,48,0.28);
  border-radius: $r-full;
  padding: 8rpx 18rpx;
}
.home__hero-badge-dot {
  width: 10rpx; height: 10rpx;
  background: $cf-lime; border-radius: $r-full;
  animation: pulse 2s ease-in-out infinite;
}
.home__hero-badge-text { font-size: 20rpx; color: $cf-lime; font-weight: 600; }

.home__hero-divider { height: 0.5px; background: $cf-line; margin: 0 0 24rpx; }

.home__hero-stats { display: flex; align-items: center; }
.home__hero-stat {
  flex: 1;
  display: flex; flex-direction: column; align-items: center; gap: 6rpx;
  &:active { opacity: 0.7; }
}
.home__hero-stat-val {
  font-size: 48rpx;
  font-weight: 900;
  color: $cf-white;
  letter-spacing: -0.03em;
  line-height: 1;
}
.home__hero-stat-label { font-size: 20rpx; color: $cf-text-2; }
.home__hero-stat-sep { width: 0.5px; height: 60rpx; background: $cf-line; }

// ─── Sections ────────────────────────────────────────────────────────────────
.home__section { margin-bottom: 40rpx; }
.home__section-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 40rpx 20rpx;
}
.home__section-title {
  font-size: 28rpx; font-weight: 800;
  color: $cf-white; letter-spacing: -0.01em;
  display: block;
  padding: 0 40rpx 20rpx;
}
.home__section-row .home__section-title { padding: 0; }
.home__section-more { font-size: 22rpx; color: $cf-green; font-weight: 500; }

// ─── Date chips ──────────────────────────────────────────────────────────────
.home__date-scroll { width: 100%; }
.home__date-row { display: flex; flex-direction: row; padding: 0 32rpx; gap: 12rpx; }
.home__date-chip {
  flex-shrink: 0;
  display: flex; flex-direction: column; align-items: center;
  padding: 16rpx 20rpx; min-width: 88rpx;
  background: $cf-glass-bg;
  border-radius: $r-lg;
  border: 0.5px solid $cf-glass-border;
  gap: 4rpx;
  backdrop-filter: blur(10px);
  &--active {
    background: rgba(45,139,87,0.18);
    border-color: rgba(45,139,87,0.4);
    box-shadow: 0 0 16rpx rgba(45,139,87,0.2);
  }
}
.home__date-wd {
  font-size: 18rpx; color: $cf-text-2;
  .home__date-chip--active & { color: #4ade80; }
}
.home__date-day {
  font-size: 36rpx; font-weight: 900;
  color: $cf-white; line-height: 1;
}
.home__date-today-dot {
  width: 8rpx; height: 8rpx;
  background: $cf-lime; border-radius: $r-full;
}

// ─── Horizontal scroll ───────────────────────────────────────────────────────
.home__hscroll { width: 100%; }
.home__hrow { display: flex; flex-direction: row; padding: 0 32rpx; gap: 20rpx; }

// ─── Venue cards ─────────────────────────────────────────────────────────────
.home__venue-card {
  flex-shrink: 0; width: 300rpx;
  background: $cf-glass-bg;
  border-radius: $r-xl; overflow: hidden;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(16px);
  &:active { opacity: 0.85; }
}
.home__venue-img-wrap { position: relative; height: 190rpx; background: $cf-card-solid; }
.home__venue-img { width: 100%; height: 100%; }
.home__venue-img-overlay {
  position: absolute; bottom: 0; left: 0; right: 0; height: 100rpx;
  background: linear-gradient(to bottom, transparent, rgba(8,14,11,0.75));
}
.home__venue-self-tag {
  position: absolute; top: 14rpx; left: 14rpx;
  background: linear-gradient(135deg, $cf-green, $cf-blue);
  border-radius: $r-full; padding: 4rpx 14rpx;
}
.home__venue-self-text { font-size: 18rpx; font-weight: 700; color: #fff; }
.home__venue-avail {
  position: absolute; bottom: 14rpx; right: 14rpx;
  display: flex; align-items: center; gap: 6rpx;
  background: rgba(8,14,11,0.6); backdrop-filter: blur(8px);
  border-radius: $r-full; padding: 6rpx 14rpx;
  border: 0.5px solid rgba(52,211,153,0.3);
  &--none { border-color: $cf-line; }
}
.home__venue-avail-dot {
  width: 8rpx; height: 8rpx; border-radius: $r-full;
  background: $cf-success;
  .home__venue-avail--none & { background: $cf-text-3; }
}
.home__venue-avail-text {
  font-size: 18rpx; font-weight: 500; color: $cf-success;
  .home__venue-avail--none & { color: $cf-text-3; }
}
.home__venue-info { padding: 16rpx 18rpx 20rpx; }
.home__venue-name { font-size: 26rpx; font-weight: 700; color: $cf-white; display: block; }
.home__venue-meta { font-size: 20rpx; color: $cf-text-2; margin-top: 4rpx; display: block; }
.home__venue-price {
  font-size: 28rpx; font-weight: 800; color: $cf-lime;
  margin-top: 10rpx; display: block;
}
.home__venue-price-u { font-size: 18rpx; font-weight: 400; color: $cf-text-2; }

// ─── Coach cards ─────────────────────────────────────────────────────────────
.home__coach-card {
  flex-shrink: 0; width: 200rpx;
  background: $cf-glass-bg;
  border-radius: $r-xl; padding: 24rpx 20rpx;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(16px);
  display: flex; flex-direction: column; align-items: center; gap: 10rpx;
  &:active { opacity: 0.85; }
}
.home__coach-avatar {
  width: 100rpx; height: 100rpx;
  border-radius: $r-full; background: $cf-card-solid;
}
.home__coach-level-ring {
  width: 108rpx; height: 108rpx;
  border-radius: $r-full;
  border: 2.5rpx solid;
  position: absolute;
  top: 24rpx; // adjusted inside card, this is a pseudo concept
  // Note: for proper ring positioning use a container
}
.home__coach-name { font-size: 26rpx; font-weight: 700; color: $cf-white; }
.home__coach-cert {
  background: rgba(45,139,87,0.15);
  border: 0.5px solid rgba(45,139,87,0.3);
  border-radius: $r-full; padding: 3rpx 14rpx;
}
.home__coach-cert-text { font-size: 18rpx; color: $cf-success; font-weight: 600; }
.home__coach-venue-name { font-size: 20rpx; color: $cf-text-2; text-align: center; }
.home__coach-price { font-size: 24rpx; font-weight: 700; color: $cf-lime; }

// ─── Upcoming bookings ───────────────────────────────────────────────────────
.home__booking-card {
  margin: 0 32rpx 16rpx;
  background: $cf-glass-bg;
  border-radius: $r-xl;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(16px);
  padding: 24rpx;
  display: flex; align-items: center; gap: 20rpx;
  &:active { opacity: 0.85; }
}
.home__booking-date {
  width: 84rpx; height: 84rpx;
  background: linear-gradient(135deg, rgba(45,139,87,0.25), rgba(46,134,193,0.20));
  border-radius: $r-lg;
  border: 0.5px solid rgba(45,139,87,0.3);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; flex-shrink: 0;
}
.home__booking-month { font-size: 18rpx; color: $cf-success; font-weight: 600; }
.home__booking-day { font-size: 36rpx; font-weight: 900; color: $cf-white; line-height: 1; }
.home__booking-info { flex: 1; }
.home__booking-venue { font-size: 26rpx; font-weight: 700; color: $cf-white; display: block; }
.home__booking-detail { font-size: 22rpx; color: $cf-text-2; margin-top: 4rpx; display: block; }
.home__booking-coach-row { display: flex; align-items: center; gap: 6rpx; margin-top: 8rpx; }
.home__booking-coach-icon { font-size: 18rpx; }
.home__booking-coach { font-size: 20rpx; color: #c084fc; font-weight: 500; }
.home__booking-status-col { display: flex; flex-direction: column; align-items: center; gap: 6rpx; }
.home__booking-dot { width: 10rpx; height: 10rpx; background: $cf-success; border-radius: $r-full; }
.home__booking-status { font-size: 18rpx; color: $cf-success; font-weight: 600; }

// ─── Empty ────────────────────────────────────────────────────────────────────
.home__empty-card {
  margin: 0 32rpx;
  background: $cf-glass-bg;
  border-radius: $r-xl;
  border: 0.5px dashed $cf-line-2;
  padding: 60rpx 40rpx;
  display: flex; flex-direction: column; align-items: center; gap: 14rpx;
}
.home__empty-icon { font-size: 64rpx; }
.home__empty-text { font-size: 26rpx; color: $cf-text-2; }
.home__empty-btn {
  margin-top: 8rpx;
  background: linear-gradient(135deg, $cf-green, $cf-blue);
  border-radius: $r-full; padding: 14rpx 48rpx;
  box-shadow: 0 4rpx 20rpx $cf-green-glow;
  &:active { opacity: 0.85; }
}
.home__empty-btn-text { font-size: 26rpx; font-weight: 700; color: #fff; }
</style>
