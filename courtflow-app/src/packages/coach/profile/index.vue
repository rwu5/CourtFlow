<template>
  <view class="coach">
    <!-- Mesh background -->
    <view class="coach__mesh" />

    <!-- Hero -->
    <view class="coach__hero">
      <view class="coach__hero-overlay" />

      <!-- Back -->
      <view class="coach__back" @tap="goBack">
        <cf-icon name="chevron-left" :size="22" color="rgba(255,255,255,0.9)" />
      </view>

      <!-- Avatar -->
      <view class="coach__avatar-wrap">
        <image class="coach__avatar" :src="coach.avatar" mode="aspectFill" />
        <view class="coach__avatar-ring" :style="{ borderColor: coach.color }" />
        <view class="coach__avail-badge" :class="coach.isAvailableToday ? '' : 'coach__avail-badge--off'">
          <view class="coach__avail-dot" />
          <text class="coach__avail-text">{{ coach.isAvailableToday ? '今日有课' : '今日约满' }}</text>
        </view>
      </view>

      <!-- Name + cert -->
      <text class="coach__name">{{ coach.name }} 教练</text>
      <view class="coach__cert-row">
        <view class="coach__cert-badge" :style="{ background: coach.color + '25', borderColor: coach.color + '50' }">
          <text class="coach__cert-text" :style="{ color: coach.color }">{{ coach.cert }}</text>
        </view>
        <view class="coach__years-badge">
          <text class="coach__years-text">{{ coach.yearsCoaching }}年执教</text>
        </view>
      </view>

      <!-- Stats -->
      <view class="coach__hero-stats">
        <view class="coach__hero-stat">
          <text class="coach__hero-stat-val">★ {{ coach.rating }}</text>
          <text class="coach__hero-stat-label">评分</text>
        </view>
        <view class="coach__hero-stat-sep" />
        <view class="coach__hero-stat">
          <text class="coach__hero-stat-val">{{ coach.totalSessions }}</text>
          <text class="coach__hero-stat-label">已上课</text>
        </view>
        <view class="coach__hero-stat-sep" />
        <view class="coach__hero-stat">
          <text class="coach__hero-stat-val">{{ coach.studentCount }}</text>
          <text class="coach__hero-stat-label">学员</text>
        </view>
      </view>
    </view>

    <scroll-view class="coach__scroll" scroll-y>
      <!-- Specialties -->
      <view class="coach__section">
        <text class="coach__section-title">专项技术</text>
        <view class="coach__tags-wrap">
          <view
            v-for="sp in coach.specialties"
            :key="sp.label"
            class="coach__tag"
            :style="{ background: sp.color + '18', borderColor: sp.color + '35' }"
          >
            <text class="coach__tag-text" :style="{ color: sp.color }">{{ sp.label }}</text>
          </view>
        </view>
      </view>

      <!-- Bio -->
      <view class="coach__section">
        <text class="coach__section-title">教练简介</text>
        <text class="coach__bio">{{ coach.bio }}</text>
      </view>

      <!-- My venues -->
      <view class="coach__section">
        <text class="coach__section-title">驻场场馆</text>
        <view class="coach__venues-list">
          <view
            v-for="v in coach.venues"
            :key="v.id"
            class="coach__venue-row"
            @tap="goVenue(v.id)"
          >
            <view class="coach__venue-icon-wrap">
              <cf-icon name="building" :size="20" color="#2D8B57" />
            </view>
            <view class="coach__venue-info">
              <text class="coach__venue-name">{{ v.name }}</text>
              <text class="coach__venue-address">{{ v.district }} · {{ v.distanceText }}</text>
            </view>
            <cf-icon name="chevron-right" :size="18" color="rgba(255,255,255,0.3)" />
          </view>
        </view>
      </view>

      <!-- Available slots -->
      <view class="coach__section">
        <view class="coach__avail-header">
          <text class="coach__section-title">可预约时段</text>
          <scroll-view class="coach__date-scroll" scroll-x>
            <view class="coach__date-row">
              <view
                v-for="d in dateTabs"
                :key="d.dateStr"
                class="coach__date-tab"
                :class="{ 'coach__date-tab--active': selectedDate === d.dateStr }"
                @tap="selectedDate = d.dateStr"
              >
                <text class="coach__date-wd">{{ d.weekday }}</text>
                <text class="coach__date-day">{{ d.day }}</text>
              </view>
            </view>
          </scroll-view>
        </view>

        <view class="coach__slots-grid">
          <view
            v-for="slot in availableSlots"
            :key="slot.time"
            class="coach__slot"
            :class="{
              'coach__slot--selected': selectedSlot === slot.time,
              'coach__slot--booked': slot.isBooked
            }"
            @tap="!slot.isBooked && (selectedSlot = slot.time)"
          >
            <text class="coach__slot-time">{{ slot.time }}</text>
            <text v-if="!slot.isBooked" class="coach__slot-price">¥{{ slot.price }}</text>
            <text v-else class="coach__slot-booked">已约</text>
          </view>
        </view>
      </view>

      <!-- Price breakdown -->
      <view class="coach__section">
        <text class="coach__section-title">费用说明</text>
        <view class="coach__price-rows">
          <view class="coach__price-row">
            <text class="coach__price-label">教练课时费</text>
            <text class="coach__price-val">¥{{ coach.pricePerHour }}/时</text>
          </view>
          <view class="coach__price-row">
            <text class="coach__price-label">场地费</text>
            <text class="coach__price-val">¥{{ courtFee }}/时</text>
          </view>
          <view class="coach__price-divider" />
          <view class="coach__price-row">
            <text class="coach__price-label coach__price-label--total">预计合计</text>
            <text class="coach__price-val coach__price-val--total">¥{{ totalEstimate }}/时</text>
          </view>
        </view>
      </view>

      <!-- Reviews preview -->
      <view class="coach__section">
        <view class="coach__reviews-header">
          <text class="coach__section-title">学员评价</text>
          <text class="coach__rating-big">★ {{ coach.rating }}</text>
        </view>
        <view v-for="r in coach.reviews" :key="r.id" class="coach__review-card">
          <view class="coach__review-top">
            <image class="coach__review-avatar" :src="r.avatar" mode="aspectFill" />
            <view class="coach__review-meta">
              <text class="coach__review-name">{{ r.name }}</text>
              <view class="coach__review-stars">
                <text v-for="i in 5" :key="i" class="coach__review-star" :class="i <= r.stars ? '' : 'coach__review-star--empty'">★</text>
              </view>
            </view>
            <text class="coach__review-date">{{ r.date }}</text>
          </view>
          <text class="coach__review-text">{{ r.text }}</text>
        </view>
      </view>

      <view style="height: 200rpx;" />
    </scroll-view>

    <!-- Book footer -->
    <view class="coach__footer">
      <view class="coach__footer-inner">
        <view class="coach__footer-price-wrap">
          <text class="coach__footer-label">教练费起</text>
          <text class="coach__footer-price">¥{{ coach.pricePerHour }}<text class="coach__footer-price-u">/时</text></text>
        </view>
        <view class="coach__book-btn" :class="{ 'coach__book-btn--disabled': !selectedSlot }" @tap="bookCoach">
          <text class="coach__book-btn-text">{{ selectedSlot ? '预约课程' : '选择时段' }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'

const pages = getCurrentPages()
const currentPage = pages[pages.length - 1] as any
const coachId = currentPage.options?.id ?? 'c1'

const selectedDate = ref('')
const selectedSlot = ref('')
const courtFee = ref(120)

const coach = ref({
  id: coachId,
  name: '张明',
  cert: 'ITF L2',
  avatar: '/static/coach-placeholder.jpg',
  color: '#2D8B57',
  yearsCoaching: 8,
  rating: 4.9,
  totalSessions: 328,
  studentCount: 86,
  isAvailableToday: true,
  pricePerHour: 300,
  bio: '前全国青年赛事冠军，拥有 ITF Level 2 国际网球教练认证，专注底线技术与比赛策略训练。曾培养多名青少年参加省级联赛并获奖。教学风格注重技术分解与实战结合，适合初中级球员快速进阶。',
  specialties: [
    { label: '发球技术', color: '#2D8B57' },
    { label: '底线进攻', color: '#2E86C1' },
    { label: '比赛策略', color: '#D4652A' },
    { label: '青少年训练', color: '#7B4FA0' },
  ],
  venues: [
    { id:'1', name:'卓越网球中心', district:'朝阳', distanceText:'1.2km' },
    { id:'3', name:'望京体育公园', district:'朝阳', distanceText:'3.1km' },
  ],
  reviews: [
    { id:'r1', name:'李同学', avatar:'/static/default-avatar.png', stars:5,
      date:'3月12日', text:'张教练非常专业，发球动作改了很多，很有针对性！' },
    { id:'r2', name:'王同学', avatar:'/static/default-avatar.png', stars:5,
      date:'3月8日', text:'讲解清晰，每节课都有明显进步，强烈推荐！' },
  ],
})

const totalEstimate = computed(() => coach.value.pricePerHour + courtFee.value)

const dateTabs = computed(() => {
  const wds = ['日','一','二','三','四','五','六']
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() + i)
    const pad = (n: number) => String(n).padStart(2,'0')
    return {
      dateStr: `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`,
      weekday: i === 0 ? '今' : `周${wds[d.getDay()]}`,
      day: d.getDate(),
    }
  })
})

const availableSlots = ref([
  { time: '09:00', price: 300, isBooked: false },
  { time: '10:00', price: 300, isBooked: true },
  { time: '11:00', price: 300, isBooked: false },
  { time: '14:00', price: 350, isBooked: false },
  { time: '15:00', price: 350, isBooked: true },
  { time: '16:00', price: 350, isBooked: false },
  { time: '19:00', price: 400, isBooked: false },
  { time: '20:00', price: 400, isBooked: false },
])

if (dateTabs.value.length) selectedDate.value = dateTabs.value[0].dateStr

function bookCoach() {
  if (!selectedSlot.value) return
  uni.navigateTo({
    url: `/packages/booking/order/index?coachId=${coachId}&slot=${selectedSlot.value}&type=coach`,
  })
}

function goVenue(id: string) {
  uni.navigateTo({ url: `/packages/venue/detail/index?id=${id}` })
}

function goBack() { uni.navigateBack() }
</script>

<style lang="scss">
@import '@/uni.scss';

.coach {
  background: $cf-bg;
  min-height: 100vh;
  position: relative;
}

.coach__mesh {
  position: fixed; top: 0; left: 0; right: 0; height: 700rpx;
  background:
    radial-gradient(ellipse at 50% 0%, rgba(45,139,87,0.30) 0%, transparent 55%),
    radial-gradient(ellipse at 90% 30%, rgba(46,134,193,0.20) 0%, transparent 50%),
    radial-gradient(ellipse at 10% 50%, rgba(123,79,160,0.15) 0%, transparent 45%);
  pointer-events: none; z-index: 0;
  animation: meshBreathe 6s ease-in-out infinite;
}

// ─── Hero ─────────────────────────────────────────────────────────────────────
.coach__hero {
  position: relative; z-index: 2;
  padding-top: var(--status-bar-height, 44px);
  padding-bottom: 40rpx;
  display: flex; flex-direction: column; align-items: center;
}
.coach__hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to bottom, transparent 0%, $cf-bg 100%);
  pointer-events: none;
}

.coach__back {
  position: absolute; top: calc(var(--status-bar-height, 44px) + 12rpx); left: 32rpx;
  width: 72rpx; height: 72rpx;
  background: $cf-glass-bg; border-radius: $r-full;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center;
  z-index: 5;
}
.coach__back-icon { font-size: 44rpx; color: $cf-white; font-weight: 300; }

.coach__avatar-wrap {
  position: relative; width: 160rpx; height: 160rpx;
  margin-top: 24rpx; margin-bottom: 28rpx;
}
.coach__avatar {
  width: 160rpx; height: 160rpx;
  border-radius: $r-full; background: $cf-card-solid;
}
.coach__avatar-ring {
  position: absolute; inset: -5rpx;
  border-radius: $r-full; border: 3rpx solid;
}
.coach__avail-badge {
  position: absolute; bottom: -8rpx; left: 50%; transform: translateX(-50%);
  display: flex; align-items: center; gap: 6rpx;
  background: rgba(8,14,11,0.8); backdrop-filter: blur(8px);
  border: 0.5px solid rgba(52,211,153,0.4);
  border-radius: $r-full; padding: 5rpx 14rpx;
  white-space: nowrap;
  &--off { border-color: $cf-line; }
}
.coach__avail-dot {
  width: 8rpx; height: 8rpx; background: $cf-success; border-radius: $r-full;
  animation: pulse 2s ease-in-out infinite;
  .coach__avail-badge--off & { background: $cf-text-3; animation: none; }
}
.coach__avail-text {
  font-size: 18rpx; color: $cf-success; font-weight: 600;
  .coach__avail-badge--off & { color: $cf-text-3; }
}

.coach__name {
  font-size: 48rpx; font-weight: 900; color: $cf-white;
  letter-spacing: -0.02em;
}
.coach__cert-row {
  display: flex; align-items: center; gap: 12rpx;
  margin-top: 12rpx; margin-bottom: 32rpx;
}
.coach__cert-badge { border: 0.5px solid; border-radius: $r-full; padding: 5rpx 18rpx; }
.coach__cert-text { font-size: 20rpx; font-weight: 700; }
.coach__years-badge {
  background: rgba(255,255,255,0.07); border: 0.5px solid $cf-glass-border;
  border-radius: $r-full; padding: 5rpx 18rpx;
}
.coach__years-text { font-size: 20rpx; color: $cf-text-2; }

.coach__hero-stats {
  display: flex; align-items: center;
  background: $cf-glass-bg; border: 0.5px solid $cf-glass-border;
  border-radius: $r-xl; backdrop-filter: blur(12px);
  padding: 20rpx 48rpx; gap: 0;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.2);
}
.coach__hero-stat { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6rpx; }
.coach__hero-stat-val { font-size: 36rpx; font-weight: 900; color: $cf-white; }
.coach__hero-stat-label { font-size: 18rpx; color: $cf-text-2; }
.coach__hero-stat-sep { width: 0.5px; height: 50rpx; background: $cf-line; }

// ─── Scroll content ───────────────────────────────────────────────────────────
.coach__scroll { position: relative; z-index: 1; }

.coach__section {
  margin: 0 32rpx 16rpx;
  background: $cf-glass-bg;
  border-radius: $r-xl; padding: 24rpx 28rpx;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(16px);
}
.coach__section-title {
  font-size: 22rpx; font-weight: 700; color: $cf-text-2;
  letter-spacing: 0.06em; display: block; margin-bottom: 18rpx;
}

// Specialties
.coach__tags-wrap { display: flex; flex-wrap: wrap; gap: 12rpx; }
.coach__tag { border: 0.5px solid; border-radius: $r-full; padding: 8rpx 20rpx; }
.coach__tag-text { font-size: 22rpx; font-weight: 600; }

// Bio
.coach__bio { font-size: 26rpx; color: $cf-text-2; line-height: 1.7; }

// Venues
.coach__venues-list { display: flex; flex-direction: column; gap: 12rpx; }
.coach__venue-row {
  display: flex; align-items: center; gap: 16rpx;
  background: rgba(255,255,255,0.04); border-radius: $r-lg;
  padding: 16rpx 20rpx;
  border: 0.5px solid $cf-line;
  &:active { opacity: 0.8; }
}
.coach__venue-icon-wrap {
  width: 56rpx; height: 56rpx;
  background: rgba(45,139,87,0.14); border-radius: $r-md;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.coach__venue-icon { font-size: 26rpx; }
.coach__venue-info { flex: 1; }
.coach__venue-name { font-size: 26rpx; font-weight: 600; color: $cf-white; display: block; }
.coach__venue-address { font-size: 20rpx; color: $cf-text-2; margin-top: 2rpx; display: block; }
.coach__venue-chevron { font-size: 36rpx; color: $cf-text-2; }

// Slot picker
.coach__avail-header { margin-bottom: 16rpx; }
.coach__date-scroll { width: 100%; margin-top: 12rpx; }
.coach__date-row { display: flex; flex-direction: row; gap: 10rpx; padding-bottom: 4rpx; }
.coach__date-tab {
  flex-shrink: 0; min-width: 80rpx;
  padding: 12rpx 14rpx;
  background: rgba(255,255,255,0.04); border-radius: $r-md;
  border: 0.5px solid $cf-line;
  display: flex; flex-direction: column; align-items: center; gap: 4rpx;
  &--active { background: rgba(45,139,87,0.18); border-color: rgba(45,139,87,0.4); }
}
.coach__date-wd {
  font-size: 17rpx; color: $cf-text-2;
  .coach__date-tab--active & { color: #4ade80; }
}
.coach__date-day { font-size: 28rpx; font-weight: 800; color: $cf-white; line-height: 1; }

.coach__slots-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
}
.coach__slot {
  background: rgba(255,255,255,0.05);
  border-radius: $r-md;
  border: 0.5px solid $cf-line;
  padding: 14rpx 8rpx;
  display: flex; flex-direction: column; align-items: center; gap: 4rpx;
  &--selected {
    background: rgba(45,139,87,0.2);
    border-color: rgba(45,139,87,0.5);
    box-shadow: 0 0 16rpx rgba(45,139,87,0.25);
  }
  &--booked { opacity: 0.35; }
  &:not(&--booked):active { opacity: 0.75; }
}
.coach__slot-time { font-size: 22rpx; font-weight: 700; color: $cf-white; }
.coach__slot-price { font-size: 18rpx; color: $cf-lime; font-weight: 600; }
.coach__slot-booked { font-size: 18rpx; color: $cf-text-3; }

// Price breakdown
.coach__price-rows { display: flex; flex-direction: column; gap: 14rpx; }
.coach__price-row { display: flex; justify-content: space-between; align-items: center; }
.coach__price-label { font-size: 26rpx; color: $cf-text-2; &--total { color: $cf-white; font-weight: 700; } }
.coach__price-val { font-size: 26rpx; color: $cf-white; font-weight: 600; &--total { font-size: 36rpx; font-weight: 900; color: $cf-lime; } }
.coach__price-divider { height: 0.5px; background: $cf-line; margin: 4rpx 0; }

// Reviews
.coach__reviews-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16rpx; }
.coach__rating-big { font-size: 36rpx; font-weight: 900; color: $cf-amber; }
.coach__review-card {
  background: rgba(255,255,255,0.04); border-radius: $r-lg;
  border: 0.5px solid $cf-line; padding: 16rpx 20rpx;
  margin-bottom: 12rpx;
}
.coach__review-top { display: flex; align-items: center; gap: 14rpx; margin-bottom: 10rpx; }
.coach__review-avatar { width: 48rpx; height: 48rpx; border-radius: $r-full; background: $cf-card-solid; }
.coach__review-meta { flex: 1; }
.coach__review-name { font-size: 22rpx; font-weight: 600; color: $cf-white; display: block; }
.coach__review-stars { display: flex; gap: 2rpx; margin-top: 4rpx; }
.coach__review-star { font-size: 18rpx; color: $cf-amber; &--empty { color: $cf-text-3; } }
.coach__review-date { font-size: 18rpx; color: $cf-text-3; }
.coach__review-text { font-size: 24rpx; color: $cf-text-2; line-height: 1.6; }

// ─── Footer ──────────────────────────────────────────────────────────────────
.coach__footer {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: rgba(13,23,18,0.92);
  border-top: 0.5px solid $cf-glass-border-2;
  backdrop-filter: blur(20px);
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 10;
}
.coach__footer-inner {
  display: flex; align-items: center;
  padding: 20rpx 32rpx; gap: 20rpx;
}
.coach__footer-price-wrap { flex: 1; }
.coach__footer-label { font-size: 20rpx; color: $cf-text-2; display: block; }
.coach__footer-price { font-size: 44rpx; font-weight: 900; color: $cf-lime; letter-spacing: -0.02em; }
.coach__footer-price-u { font-size: 22rpx; font-weight: 400; color: $cf-text-2; }
.coach__book-btn {
  background: linear-gradient(135deg, $cf-green, $cf-blue);
  border-radius: $r-full;
  padding: 0 48rpx; height: 88rpx;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6rpx 28rpx $cf-green-glow;
  &--disabled { opacity: 0.5; }
  &:not(&--disabled):active { opacity: 0.85; }
}
.coach__book-btn-text { font-size: 28rpx; font-weight: 700; color: #fff; letter-spacing: 0.02em; }
</style>
