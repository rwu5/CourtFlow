<template>
  <view class="courses">
    <!-- Mesh background -->
    <view class="courses__mesh" />
    <view class="courses__statusbar" />

    <!-- Header -->
    <view class="courses__header">
      <text class="courses__title">课程 & 教练</text>
      <text class="courses__subtitle">在最近的场馆找到你的专属教练</text>
    </view>

    <!-- Search bar -->
    <view class="courses__search-wrap">
      <view class="courses__search">
        <cf-icon name="search" :size="20" color="rgba(255,255,255,0.35)" />
        <input
          v-model="searchQuery"
          class="courses__search-input"
          placeholder="搜索教练名、课程类型、场馆…"
          placeholder-class="courses__search-ph"
        />
      </view>
    </view>

    <!-- Category tabs -->
    <view class="courses__cats">
      <view
        v-for="cat in categories"
        :key="cat.key"
        class="courses__cat"
        :class="{ 'courses__cat--active': activeCat === cat.key }"
        @tap="activeCat = cat.key"
      >
        <cf-icon :name="cat.icon" :size="18" :color="activeCat === cat.key ? '#B8D430' : 'rgba(255,255,255,0.45)'" />
        <text class="courses__cat-label">{{ cat.label }}</text>
      </view>
    </view>

    <scroll-view class="courses__scroll" scroll-y>
      <!-- Featured Coaches section -->
      <view class="courses__section">
        <view class="courses__section-row">
          <text class="courses__section-title">附近教练</text>
          <view class="courses__section-filter" @tap="toggleSortCoach">
            <text class="courses__section-filter-text">{{ coachSortLabel }} ⇅</text>
          </view>
        </view>

        <scroll-view class="courses__hscroll" scroll-x>
          <view class="courses__coaches-row">
            <view
              v-for="c in filteredCoaches"
              :key="c.id"
              class="courses__coach-card"
              @tap="goCoachProfile(c.id)"
            >
              <!-- Avatar with level ring -->
              <view class="courses__coach-avatar-wrap">
                <image class="courses__coach-avatar" :src="c.avatar" mode="aspectFill" />
                <view class="courses__coach-ring" :style="{ borderColor: c.color }" />
                <view class="courses__coach-avail-dot" :class="c.isAvailableToday ? '' : 'courses__coach-avail-dot--off'" />
              </view>

              <text class="courses__coach-name">{{ c.name }}</text>

              <view class="courses__coach-cert-row">
                <view class="courses__coach-cert-badge" :style="{ background: c.color + '22', borderColor: c.color + '44' }">
                  <text class="courses__coach-cert-text" :style="{ color: c.color }">{{ c.cert }}</text>
                </view>
              </view>

              <view class="courses__coach-stats">
                <text class="courses__coach-rating">★ {{ c.rating }}</text>
                <text class="courses__coach-sessions">{{ c.totalSessions }}节课</text>
              </view>

              <text class="courses__coach-venue">{{ c.venueName }}</text>
              <text class="courses__coach-price">¥{{ c.pricePerHour }}<text class="courses__coach-price-u">/时</text></text>

              <view class="courses__coach-book-btn" @tap.stop="quickBook(c.id)">
                <text class="courses__coach-book-text">预约</text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- Course listings -->
      <view class="courses__section">
        <view class="courses__section-row">
          <text class="courses__section-title">{{ categoryLabel }}</text>
          <text class="courses__courses-count">{{ filteredCourses.length }} 个课程</text>
        </view>

        <view class="courses__list">
          <view
            v-for="course in filteredCourses"
            :key="course.id"
            class="courses__course-card"
            @tap="goCourseDetail(course.id)"
          >
            <!-- Left: coach avatar + info -->
            <view class="courses__course-left">
              <view class="courses__course-avatar-wrap">
                <image class="courses__course-avatar" :src="course.coachAvatar" mode="aspectFill" />
                <view class="courses__course-type-dot" :style="{ background: course.typeColor }" />
              </view>
            </view>

            <!-- Center: course info -->
            <view class="courses__course-body">
              <view class="courses__course-name-row">
                <text class="courses__course-name">{{ course.name }}</text>
                <view class="courses__course-type-badge" :style="{ background: course.typeColor + '20', borderColor: course.typeColor + '40' }">
                  <text class="courses__course-type-text" :style="{ color: course.typeColor }">{{ course.typeLabel }}</text>
                </view>
              </view>

              <text class="courses__course-coach">{{ course.coachName }} · {{ course.coachCert }}</text>

              <!-- Venue chip -->
              <view class="courses__course-venue-row">
                <cf-icon name="location" :size="16" color="rgba(255,255,255,0.4)" />
                <text class="courses__course-venue">{{ course.venueName }}</text>
              </view>

              <!-- Time + spots -->
              <view class="courses__course-meta-row">
                <view class="courses__course-time-chip">
                  <cf-icon name="calendar" :size="14" color="rgba(255,255,255,0.5)" />
                  <text class="courses__course-time">{{ course.schedule }}</text>
                </view>
                <view class="courses__course-spots" :class="course.spotsLeft <= 2 ? 'courses__course-spots--urgent' : ''">
                  <text class="courses__course-spots-text">余 {{ course.spotsLeft }} 位</text>
                </view>
              </view>
            </view>

            <!-- Right: price + action -->
            <view class="courses__course-right">
              <text class="courses__course-price">¥{{ course.price }}</text>
              <text class="courses__course-price-unit">/次</text>
              <view class="courses__course-arrow">
                <cf-icon name="chevron-right" :size="18" color="rgba(255,255,255,0.4)" />
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- Venue with coaches section -->
      <view class="courses__section">
        <text class="courses__section-title">按场馆找教练</text>
        <view class="courses__venues-list">
          <view
            v-for="v in venuesWithCoaches"
            :key="v.id"
            class="courses__venue-row"
            @tap="goVenueDetail(v.id)"
          >
            <view class="courses__venue-icon-wrap">
              <cf-icon name="building" :size="22" color="#2D8B57" />
            </view>
            <view class="courses__venue-info">
              <text class="courses__venue-name">{{ v.name }}</text>
              <text class="courses__venue-coaches-count">{{ v.coachCount }} 位教练在场</text>
            </view>
            <view class="courses__venue-coaches-avatars">
              <image
                v-for="(av, i) in v.coachAvatars.slice(0,3)"
                :key="i"
                class="courses__venue-coach-av"
                :style="{ left: (i * 28) + 'rpx', zIndex: 3 - i }"
                :src="av"
                mode="aspectFill"
              />
            </view>
            <cf-icon name="chevron-right" :size="18" color="rgba(255,255,255,0.3)" />
          </view>
        </view>
      </view>

      <view style="height: 160rpx;" />
    </scroll-view>

    <!-- Custom Tab Bar -->
    <cf-tab-bar current="/pages/courses/index" />
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfTabBar from '@/components/ui/CfTabBar.vue'

const searchQuery = ref('')
const activeCat = ref('all')
const coachSort = ref('distance')

const categories = [
  { key: 'all',     icon: 'ball',    label: '全部' },
  { key: 'private', icon: 'person',  label: '私教课' },
  { key: 'group',   icon: 'courses', label: '团体课' },
  { key: 'camp',    icon: 'trophy',  label: '训练营' },
]

const categoryLabel = computed(() => categories.find(c => c.key === activeCat.value)?.label ?? '全部课程')
const coachSortLabel = computed(() => coachSort.value === 'distance' ? '按距离' : '按评分')

function toggleSortCoach() {
  coachSort.value = coachSort.value === 'distance' ? 'rating' : 'distance'
}

const coaches = ref([
  { id:'c1', name:'张明', cert:'ITF L2', avatar:'/static/coach-placeholder.jpg',
    venueName:'卓越网球中心', pricePerHour:300, rating:4.9, totalSessions:328,
    isAvailableToday: true, color:'#2D8B57', specialties:['发球','底线'] },
  { id:'c2', name:'李华', cert:'LTA L3', avatar:'/static/coach-placeholder.jpg',
    venueName:'国贸球场', pricePerHour:400, rating:5.0, totalSessions:512,
    isAvailableToday: true, color:'#2E86C1', specialties:['全面','比赛策略'] },
  { id:'c3', name:'王芳', cert:'ITF L1', avatar:'/static/coach-placeholder.jpg',
    venueName:'望京体育公园', pricePerHour:250, rating:4.7, totalSessions:156,
    isAvailableToday: false, color:'#7B4FA0', specialties:['初学者','青少年'] },
  { id:'c4', name:'陈刚', cert:'ITF L2', avatar:'/static/coach-placeholder.jpg',
    venueName:'卓越网球中心', pricePerHour:350, rating:4.8, totalSessions:241,
    isAvailableToday: true, color:'#D4652A', specialties:['步法','截击'] },
])

const filteredCoaches = computed(() => {
  let list = coaches.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(c => c.name.includes(q) || c.venueName.includes(q))
  }
  if (coachSort.value === 'rating') return [...list].sort((a,b) => b.rating - a.rating)
  return list
})

const allCourses = ref([
  { id:'cr1', name:'发球专项训练', typeLabel:'私教课', typeColor:'#2D8B57',
    coachName:'张明', coachCert:'ITF L2', coachAvatar:'/static/coach-placeholder.jpg',
    venueName:'卓越网球中心', schedule:'周二 / 周四 10:00',
    price:280, spotsLeft:1, type:'private' },
  { id:'cr2', name:'网球入门8节课', typeLabel:'团体课', typeColor:'#2E86C1',
    coachName:'王芳', coachCert:'ITF L1', coachAvatar:'/static/coach-placeholder.jpg',
    venueName:'望京体育公园', schedule:'周末 09:00',
    price:160, spotsLeft:4, type:'group' },
  { id:'cr3', name:'暑期网球训练营', typeLabel:'训练营', typeColor:'#D4652A',
    coachName:'李华', coachCert:'LTA L3', coachAvatar:'/static/coach-placeholder.jpg',
    venueName:'国贸球场', schedule:'7/1–7/14 每天',
    price:3800, spotsLeft:6, type:'camp' },
  { id:'cr4', name:'底线进阶私教', typeLabel:'私教课', typeColor:'#2D8B57',
    coachName:'陈刚', coachCert:'ITF L2', coachAvatar:'/static/coach-placeholder.jpg',
    venueName:'卓越网球中心', schedule:'灵活约课',
    price:320, spotsLeft:3, type:'private' },
])

const filteredCourses = computed(() => {
  let list = allCourses.value
  if (activeCat.value !== 'all') list = list.filter(c => c.type === activeCat.value)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(c => c.name.includes(q) || c.coachName.includes(q) || c.venueName.includes(q))
  }
  return list
})

const venuesWithCoaches = ref([
  { id:'1', name:'卓越网球中心', coachCount:3,
    coachAvatars:['/static/coach-placeholder.jpg','/static/coach-placeholder.jpg','/static/coach-placeholder.jpg'] },
  { id:'2', name:'国贸球场', coachCount:1,
    coachAvatars:['/static/coach-placeholder.jpg'] },
  { id:'3', name:'望京体育公园', coachCount:2,
    coachAvatars:['/static/coach-placeholder.jpg','/static/coach-placeholder.jpg'] },
])

function goCoachProfile(id: string) {
  uni.navigateTo({ url: `/packages/coach/profile/index?id=${id}` })
}

function quickBook(coachId: string) {
  uni.navigateTo({ url: `/packages/coach/profile/index?id=${coachId}&quickBook=1` })
}

function goCourseDetail(id: string) {
  const course = allCourses.value.find(c => c.id === id)
  if (course) {
    uni.navigateTo({ url: `/packages/coach/profile/index?courseId=${id}` })
  }
}

function goVenueDetail(id: string) {
  uni.navigateTo({ url: `/packages/venue/detail/index?id=${id}` })
}
</script>

<style lang="scss">
@import '@/uni.scss';

.courses {
  background: $cf-bg;
  min-height: 100vh;
  position: relative;
}

.courses__mesh {
  position: fixed; top: 0; left: 0; right: 0; height: 600rpx;
  background:
    radial-gradient(ellipse at 70% 10%, rgba(123,79,160,0.22) 0%, transparent 50%),
    radial-gradient(ellipse at 10% 30%, rgba(46,134,193,0.20) 0%, transparent 55%),
    radial-gradient(ellipse at 50% 70%, rgba(45,139,87,0.12) 0%, transparent 45%);
  pointer-events: none; z-index: 0;
  animation: meshBreathe 7s ease-in-out infinite;
}

.courses__statusbar { height: var(--status-bar-height, 44px); position: relative; z-index: 2; }

// ─── Header ──────────────────────────────────────────────────────────────────
.courses__header { padding: 16rpx 40rpx 24rpx; position: relative; z-index: 2; }
.courses__title {
  display: block;
  font-size: 44rpx; font-weight: 900;
  color: $cf-white; letter-spacing: -0.02em;
}
.courses__subtitle { font-size: 22rpx; color: $cf-text-2; margin-top: 6rpx; display: block; }

// ─── Search ──────────────────────────────────────────────────────────────────
.courses__search-wrap { padding: 0 32rpx 20rpx; position: relative; z-index: 2; }
.courses__search {
  display: flex; align-items: center; gap: 16rpx;
  background: $cf-glass-bg;
  border-radius: $r-xl;
  border: 0.5px solid $cf-glass-border-2;
  backdrop-filter: blur(20px);
  padding: 0 24rpx;
  height: 80rpx;
}
.courses__search-icon { font-size: 26rpx; flex-shrink: 0; }
.courses__search-input { flex: 1; font-size: 26rpx; color: $cf-white; background: transparent; height: 80rpx; }
.courses__search-ph { color: $cf-text-3; font-size: 26rpx; }

// ─── Category tabs ───────────────────────────────────────────────────────────
.courses__cats {
  display: flex; flex-direction: row;
  padding: 0 32rpx 24rpx;
  gap: 14rpx;
  position: relative; z-index: 2;
}
.courses__cat {
  flex: 1;
  display: flex; flex-direction: column; align-items: center;
  padding: 16rpx 12rpx;
  background: $cf-glass-bg;
  border-radius: $r-lg;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(10px);
  gap: 6rpx;
  &--active {
    background: rgba(45,139,87,0.16);
    border-color: rgba(45,139,87,0.38);
    box-shadow: 0 0 20rpx rgba(45,139,87,0.18);
  }
}
.courses__cat-icon { font-size: 28rpx; }
.courses__cat-label {
  font-size: 20rpx; color: $cf-text-2; font-weight: 500;
  .courses__cat--active & { color: #4ade80; font-weight: 700; }
}

// ─── Scroll ──────────────────────────────────────────────────────────────────
.courses__scroll { position: relative; z-index: 1; }

// ─── Section ─────────────────────────────────────────────────────────────────
.courses__section { margin-bottom: 40rpx; }
.courses__section-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 40rpx 20rpx;
}
.courses__section-title {
  font-size: 28rpx; font-weight: 800; color: $cf-white;
  display: block; padding: 0 40rpx 20rpx;
}
.courses__section-row .courses__section-title { padding: 0; }
.courses__section-filter {
  background: $cf-glass-bg;
  border: 0.5px solid $cf-glass-border;
  border-radius: $r-full; padding: 6rpx 20rpx;
}
.courses__section-filter-text { font-size: 20rpx; color: $cf-green; font-weight: 500; }
.courses__courses-count { font-size: 22rpx; color: $cf-text-2; }

// ─── Coaches horizontal ──────────────────────────────────────────────────────
.courses__hscroll { width: 100%; }
.courses__coaches-row { display: flex; flex-direction: row; padding: 4rpx 32rpx 12rpx; gap: 16rpx; }

.courses__coach-card {
  flex-shrink: 0; width: 210rpx;
  background: $cf-glass-bg;
  border-radius: $r-xl; padding: 24rpx 20rpx 20rpx;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(16px);
  display: flex; flex-direction: column; align-items: center; gap: 10rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.15);
  &:active { opacity: 0.85; }
}

.courses__coach-avatar-wrap {
  position: relative; width: 100rpx; height: 100rpx; margin-bottom: 4rpx;
}
.courses__coach-avatar {
  width: 100rpx; height: 100rpx;
  border-radius: $r-full; background: $cf-card-solid;
}
.courses__coach-ring {
  position: absolute; inset: -4rpx;
  border-radius: $r-full;
  border: 2.5rpx solid;
}
.courses__coach-avail-dot {
  position: absolute; bottom: 4rpx; right: 4rpx;
  width: 18rpx; height: 18rpx;
  background: $cf-success; border-radius: $r-full;
  border: 2.5rpx solid $cf-bg;
  &--off { background: $cf-text-3; }
}
.courses__coach-name { font-size: 26rpx; font-weight: 700; color: $cf-white; }
.courses__coach-cert-row { display: flex; }
.courses__coach-cert-badge {
  border: 0.5px solid;
  border-radius: $r-full; padding: 3rpx 14rpx;
}
.courses__coach-cert-text { font-size: 18rpx; font-weight: 700; }
.courses__coach-stats { display: flex; align-items: center; gap: 12rpx; }
.courses__coach-rating { font-size: 20rpx; color: $cf-amber; font-weight: 600; }
.courses__coach-sessions { font-size: 18rpx; color: $cf-text-2; }
.courses__coach-venue { font-size: 18rpx; color: $cf-text-2; text-align: center; line-height: 1.3; }
.courses__coach-price { font-size: 26rpx; font-weight: 800; color: $cf-lime; }
.courses__coach-price-u { font-size: 18rpx; font-weight: 400; color: $cf-text-2; }
.courses__coach-book-btn {
  width: 100%; height: 60rpx;
  background: linear-gradient(135deg, $cf-green, $cf-blue);
  border-radius: $r-full;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4rpx 16rpx $cf-green-glow;
  &:active { opacity: 0.85; }
}
.courses__coach-book-text { font-size: 22rpx; font-weight: 700; color: #fff; }

// ─── Course cards ─────────────────────────────────────────────────────────────
.courses__list { display: flex; flex-direction: column; gap: 16rpx; padding: 0 32rpx; }

.courses__course-card {
  background: $cf-glass-bg;
  border-radius: $r-xl;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(16px);
  padding: 24rpx;
  display: flex; align-items: flex-start; gap: 16rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.14);
  &:active { opacity: 0.85; }
}

.courses__course-left { flex-shrink: 0; }
.courses__course-avatar-wrap { position: relative; width: 80rpx; height: 80rpx; }
.courses__course-avatar { width: 80rpx; height: 80rpx; border-radius: $r-lg; background: $cf-card-solid; }
.courses__course-type-dot {
  position: absolute; bottom: -4rpx; right: -4rpx;
  width: 24rpx; height: 24rpx;
  border-radius: $r-full;
  border: 2.5rpx solid $cf-bg;
}

.courses__course-body { flex: 1; min-width: 0; }
.courses__course-name-row { display: flex; align-items: center; gap: 10rpx; flex-wrap: wrap; margin-bottom: 6rpx; }
.courses__course-name { font-size: 26rpx; font-weight: 700; color: $cf-white; flex: 1; }
.courses__course-type-badge {
  border: 0.5px solid; border-radius: $r-full; padding: 3rpx 12rpx; flex-shrink: 0;
}
.courses__course-type-text { font-size: 18rpx; font-weight: 700; }
.courses__course-coach { font-size: 21rpx; color: $cf-text-2; display: block; margin-bottom: 8rpx; }
.courses__course-venue-row { display: flex; align-items: center; gap: 6rpx; margin-bottom: 10rpx; }
.courses__course-venue-icon { font-size: 18rpx; }
.courses__course-venue { font-size: 20rpx; color: $cf-text-2; }
.courses__course-meta-row { display: flex; align-items: center; gap: 12rpx; }
.courses__course-time-chip {
  display: flex; align-items: center; gap: 6rpx;
  background: rgba(255,255,255,0.06); border-radius: $r-full; padding: 4rpx 14rpx;
}
.courses__course-time-icon { font-size: 18rpx; }
.courses__course-time { font-size: 19rpx; color: $cf-text-2; }
.courses__course-spots {
  background: rgba(52,211,153,0.12); border: 0.5px solid rgba(52,211,153,0.3);
  border-radius: $r-full; padding: 4rpx 14rpx;
  &--urgent { background: rgba(251,191,36,0.14); border-color: rgba(251,191,36,0.3); }
}
.courses__course-spots-text {
  font-size: 18rpx; color: $cf-success; font-weight: 600;
  .courses__course-spots--urgent & { color: $cf-amber; }
}

.courses__course-right {
  display: flex; flex-direction: column; align-items: flex-end;
  gap: 6rpx; flex-shrink: 0;
}
.courses__course-price { font-size: 32rpx; font-weight: 900; color: $cf-lime; }
.courses__course-price-unit { font-size: 18rpx; color: $cf-text-2; }
.courses__course-arrow {
  width: 48rpx; height: 48rpx;
  background: $cf-glass-bg; border-radius: $r-full;
  border: 0.5px solid $cf-glass-border;
  display: flex; align-items: center; justify-content: center;
}
.courses__course-arrow-text { font-size: 32rpx; color: $cf-text-2; }

// ─── Venues with coaches ─────────────────────────────────────────────────────
.courses__venues-list { display: flex; flex-direction: column; gap: 12rpx; padding: 0 32rpx; }
.courses__venue-row {
  background: $cf-glass-bg;
  border-radius: $r-xl; padding: 20rpx 24rpx;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(16px);
  display: flex; align-items: center; gap: 18rpx;
  &:active { opacity: 0.85; }
}
.courses__venue-icon-wrap {
  width: 64rpx; height: 64rpx;
  background: rgba(45,139,87,0.14); border-radius: $r-lg;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; border: 0.5px solid rgba(45,139,87,0.25);
}
.courses__venue-icon { font-size: 30rpx; }
.courses__venue-info { flex: 1; }
.courses__venue-name { font-size: 26rpx; font-weight: 700; color: $cf-white; display: block; }
.courses__venue-coaches-count { font-size: 20rpx; color: $cf-text-2; margin-top: 4rpx; display: block; }
.courses__venue-coaches-avatars { position: relative; width: 80rpx; height: 48rpx; flex-shrink: 0; }
.courses__venue-coach-av {
  width: 48rpx; height: 48rpx;
  border-radius: $r-full;
  position: absolute; top: 0;
  border: 2rpx solid $cf-bg;
  background: $cf-card-solid;
}
.courses__venue-chevron { font-size: 40rpx; color: $cf-text-2; }
</style>
