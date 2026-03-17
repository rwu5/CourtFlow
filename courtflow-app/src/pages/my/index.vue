<template>
  <view class="my">
    <!-- Mesh gradient -->
    <view class="my__mesh" />
    <view class="my__statusbar" />

    <scroll-view class="my__scroll" scroll-y>
      <!-- ── Hero ─────────────────────────────────────────────────── -->
      <view class="my__hero">
        <!-- Edit button -->
        <view class="my__edit-btn" @tap="goEditProfile">
          <CfIcon name="edit" :size="18" color="rgba(255,255,255,0.7)" />
        </view>

        <!-- Avatar with animated gradient ring -->
        <view class="my__avatar-frame" @tap="goEditProfile">
          <view class="my__avatar-ring-outer" />
          <view class="my__avatar-ring-inner" />
          <image class="my__avatar" :src="user?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
          <!-- Skill tier indicator -->
          <view class="my__avatar-tier-badge" :style="{ background: currentLevel.color }">
            <text class="my__avatar-tier-text">{{ currentLevel.short }}</text>
          </view>
        </view>

        <!-- Name -->
        <text class="my__name">{{ user?.nickname || '网球爱好者' }}</text>
        <text class="my__handle" v-if="user">@rally_{{ user.id?.slice(0,6) ?? 'user' }}</text>
        <text class="my__login-cta" v-else @tap="goLogin">登录 / 注册 →</text>

        <!-- Skill level bar -->
        <view class="my__skill-section">
          <view class="my__skill-bar">
            <view
              v-for="lv in levels"
              :key="lv.key"
              class="my__skill-pip"
              :class="{
                'my__skill-pip--active': levelIndex >= lv.index,
                'my__skill-pip--current': levelIndex === lv.index
              }"
              :style="levelIndex >= lv.index ? { background: `linear-gradient(90deg, ${lv.color1}, ${lv.color2})` } : {}"
            />
          </view>
          <view class="my__skill-label-row">
            <text class="my__skill-label-left">入门</text>
            <view class="my__skill-current-label" :style="{ left: skillPct + '%' }">
              <text class="my__skill-current-text">{{ currentLevel.label }}</text>
            </view>
            <text class="my__skill-label-right">专业</text>
          </view>
        </view>

        <!-- Stats row -->
        <view class="my__stats-glass">
          <view v-for="(stat, i) in stats" :key="stat.label" class="my__stat">
            <text class="my__stat-value">{{ stat.value }}</text>
            <text class="my__stat-label">{{ stat.label }}</text>
            <view v-if="i < stats.length - 1" class="my__stat-sep" />
          </view>
        </view>
      </view>

      <!-- ── Quick Actions ──────────────────────────────────────── -->
      <view class="my__section my__section--actions">
        <view
          v-for="action in quickActions"
          :key="action.label"
          class="my__action-card"
          @tap="action.handler"
        >
          <view class="my__action-icon-ring" :style="{ background: action.bgGrad }">
            <CfIcon :name="action.icon" :size="22" color="#fff" :stroke-width="1.5" />
          </view>
          <text class="my__action-label">{{ action.label }}</text>
          <view v-if="action.badge" class="my__action-badge">
            <text class="my__action-badge-text">{{ action.badge }}</text>
          </view>
        </view>
      </view>

      <!-- ── Recent Activity ──────────────────────────────────── -->
      <view class="my__section-card">
        <view class="my__section-head">
          <view class="my__section-head-left">
            <view class="my__section-head-dot my__section-head-dot--green" />
            <text class="my__section-head-title">最近预约</text>
          </view>
          <view class="my__section-head-more" @tap="goOrders">
            <text class="my__section-head-more-text">全部</text>
            <CfIcon name="chevron-right" :size="14" color="rgba(45,139,87,0.9)" />
          </view>
        </view>

        <view v-if="recentBookings.length > 0">
          <view
            v-for="(b, i) in recentBookings"
            :key="b.id"
            class="my__activity-row"
            :class="{ 'my__activity-row--last': i === recentBookings.length - 1 }"
            @tap="goOrderDetail(b.id)"
          >
            <view class="my__activity-icon-wrap" :class="`my__activity-icon-wrap--${b.type}`">
              <CfIcon :name="b.type === 'coach' ? 'courses' : 'court'" :size="18" :color="b.type === 'coach' ? '#2E86C1' : '#2D8B57'" :stroke-width="1.5" />
            </view>
            <view class="my__activity-info">
              <text class="my__activity-venue">{{ b.venueName }}</text>
              <text class="my__activity-detail">{{ b.detail }}</text>
            </view>
            <view class="my__activity-right">
              <view class="my__activity-status" :class="`my__activity-status--${b.status}`">
                <view class="my__activity-status-dot" />
                <text class="my__activity-status-text">{{ b.statusLabel }}</text>
              </view>
              <text class="my__activity-price">¥{{ b.total }}</text>
            </view>
          </view>
        </view>

        <view v-else class="my__activity-empty">
          <CfIcon name="calendar" :size="36" color="rgba(255,255,255,0.15)" />
          <text class="my__activity-empty-text">暂无预约记录</text>
          <view class="my__activity-empty-btn" @tap="goVenues">
            <text class="my__activity-empty-btn-text">去预订场地</text>
          </view>
        </view>
      </view>

      <!-- ── Tennis Profile ─────────────────────────────────────── -->
      <view class="my__section-card">
        <view class="my__section-head">
          <view class="my__section-head-left">
            <view class="my__section-head-dot my__section-head-dot--blue" />
            <text class="my__section-head-title">我的球员档案</text>
          </view>
          <view class="my__section-head-more" @tap="goEditProfile">
            <text class="my__section-head-more-text">编辑</text>
            <CfIcon name="edit" :size="14" color="rgba(46,134,193,0.9)" />
          </view>
        </view>

        <view class="my__tennis-grid">
          <view v-for="attr in tennisAttrs" :key="attr.label" class="my__tennis-attr">
            <view class="my__tennis-attr-icon" :style="{ background: attr.bg }">
              <CfIcon :name="attr.icon" :size="16" :color="attr.color" :stroke-width="1.6" />
            </view>
            <text class="my__tennis-attr-label">{{ attr.label }}</text>
            <text class="my__tennis-attr-value">{{ attr.value }}</text>
          </view>
        </view>
      </view>

      <!-- ── Settings ──────────────────────────────────────────── -->
      <view class="my__section-card">
        <view class="my__section-head">
          <view class="my__section-head-left">
            <view class="my__section-head-dot my__section-head-dot--grey" />
            <text class="my__section-head-title">设置</text>
          </view>
        </view>

        <view
          v-for="(item, i) in settingsItems"
          :key="item.label"
          class="my__setting-row"
          :class="{
            'my__setting-row--last': i === settingsItems.length - 1,
            'my__setting-row--danger': item.isDanger
          }"
          @tap="item.handler"
        >
          <view class="my__setting-icon-wrap" :style="{ background: item.bg }">
            <CfIcon :name="item.icon" :size="16" :color="item.color" :stroke-width="1.6" />
          </view>
          <text class="my__setting-label" :class="{ 'my__setting-label--danger': item.isDanger }">{{ item.label }}</text>
          <view class="my__setting-right">
            <text v-if="item.value" class="my__setting-value">{{ item.value }}</text>
            <CfIcon name="chevron-right" :size="16" :color="item.isDanger ? '#F04545' : 'rgba(255,255,255,0.25)'" />
          </view>
        </view>
      </view>

      <!-- App version + brand -->
      <view class="my__brand-footer">
        <text class="my__brand-name">RallyAI</text>
        <text class="my__brand-version">场馆预订 & 教练课程 · v1.0.0</text>
      </view>

      <view style="height: 160rpx;" />
    </scroll-view>

    <!-- Custom Tab Bar -->
    <cf-tab-bar current="/pages/my/index" />
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfTabBar from '@/components/ui/CfTabBar.vue'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

// ── Skill levels ──────────────────────────────────────────────────────────────
const levels = [
  { key: 'beginner',     index: 0, label: '入门',   short: 'B', color1: '#6ee7b7', color2: '#34d399' },
  { key: 'elementary',  index: 1, label: '初级',   short: 'E', color1: '#34d399', color2: '#2D8B57' },
  { key: 'intermediate',index: 2, label: '中级',   short: 'I', color1: '#2D8B57', color2: '#2E86C1' },
  { key: 'advanced',    index: 3, label: '高级',   short: 'A', color1: '#2E86C1', color2: '#7B4FA0' },
  { key: 'professional',index: 4, label: '专业',   short: 'P', color1: '#7B4FA0', color2: '#D4652A' },
]

const currentLevelKey = computed(() => user.value?.player_level ?? 'intermediate')
const levelIndex = computed(() => levels.findIndex(l => l.key === currentLevelKey.value))
const currentLevel = computed(() => levels[levelIndex.value] ?? levels[2])
const skillPct = computed(() => (levelIndex.value / (levels.length - 1)) * 80 + 10)

// ── Stats ─────────────────────────────────────────────────────────────────────
const stats = ref([
  { value: '12', label: '预约次数' },
  { value: '3', label: '教练课' },
  { value: '★4.8', label: '评分' },
])

// ── Quick actions ─────────────────────────────────────────────────────────────
const quickActions = [
  {
    icon: 'document', label: '我的订单',
    bgGrad: 'linear-gradient(135deg, #2D8B57, #1a6640)',
    badge: null,
    handler: () => uni.navigateTo({ url: '/packages/account/orders/index' }),
  },
  {
    icon: 'courses', label: '我的课程',
    bgGrad: 'linear-gradient(135deg, #2E86C1, #1a5a8a)',
    badge: null,
    handler: () => uni.switchTab({ url: '/pages/courses/index' }),
  },
  {
    icon: 'credit-card', label: '会员卡',
    bgGrad: 'linear-gradient(135deg, #D4652A, #a34a1a)',
    badge: 'NEW',
    handler: () => uni.showToast({ title: '会员功能即将上线', icon: 'none' }),
  },
  {
    icon: 'ticket', label: '优惠券',
    bgGrad: 'linear-gradient(135deg, #7B4FA0, #5a3278)',
    badge: null,
    handler: () => uni.showToast({ title: '暂无可用优惠券', icon: 'none' }),
  },
]

// ── Recent bookings ───────────────────────────────────────────────────────────
const recentBookings = ref([
  { id:'1', venueName:'卓越网球中心', detail:'1号场 · 03/15 10:00–11:00',
    type:'court', status:'confirmed', statusLabel:'已完成', total:'120' },
  { id:'2', venueName:'张明教练课', detail:'卓越网球中心 · 03/18 14:00',
    type:'coach', status:'confirmed', statusLabel:'已完成', total:'300' },
  { id:'3', venueName:'国贸球场', detail:'2号场 · 03/22 09:00–10:00',
    type:'court', status:'pending', statusLabel:'待支付', total:'150' },
])

// ── Tennis profile attrs ───────────────────────────────────────────────────────
const tennisAttrs = computed(() => [
  { label: '技术水平', value: currentLevel.value.label,
    icon: 'trophy', bg: 'rgba(45,139,87,0.15)', color: '#2D8B57' },
  { label: '持拍手', value: user.value?.dominant_hand === 'left' ? '左手' : '右手',
    icon: 'ball', bg: 'rgba(46,134,193,0.15)', color: '#2E86C1' },
  { label: '反手类型', value: user.value?.backhand_type === 'one_handed' ? '单手' : '双手',
    icon: 'court', bg: 'rgba(123,79,160,0.15)', color: '#7B4FA0' },
  { label: '球员手机', value: user.value?.phone ? user.value.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '未绑定',
    icon: 'phone', bg: 'rgba(212,101,42,0.15)', color: '#D4652A' },
])

// ── Settings ─────────────────────────────────────────────────────────────────
const settingsItems = [
  { icon: 'bell', label: '消息通知', value: '已开启',
    bg: 'rgba(45,139,87,0.15)', color: '#2D8B57', isDanger: false,
    handler: () => {} },
  { icon: 'shield', label: '隐私设置', value: '',
    bg: 'rgba(46,134,193,0.15)', color: '#2E86C1', isDanger: false,
    handler: () => {} },
  { icon: 'chat', label: '联系客服', value: '',
    bg: 'rgba(123,79,160,0.15)', color: '#7B4FA0', isDanger: false,
    handler: () => uni.makePhoneCall({ phoneNumber: '400-000-0000' }) },
  { icon: 'document', label: '用户协议', value: '',
    bg: 'rgba(255,255,255,0.06)', color: 'rgba(255,255,255,0.4)', isDanger: false,
    handler: () => {} },
  { icon: 'logout', label: '退出登录', value: '',
    bg: 'rgba(240,69,69,0.12)', color: '#F04545', isDanger: true,
    handler: logout },
]

function goEditProfile() {
  if (!user.value) { goLogin(); return }
  uni.navigateTo({ url: '/packages/account/profile/index' })
}
function goLogin() { uni.navigateTo({ url: '/pages/login/index' }) }
function goOrders() { uni.navigateTo({ url: '/packages/account/orders/index' }) }
function goOrderDetail(id: string) { uni.navigateTo({ url: `/packages/booking/result/index?orderId=${id}&success=1` }) }
function goVenues() { uni.navigateTo({ url: '/packages/venue/list/index' }) }

function logout() {
  uni.showModal({
    title: '退出登录',
    content: '确定要退出当前账号吗？',
    confirmText: '退出',
    confirmColor: '#F04545',
    success: (res) => {
      if (res.confirm) {
        authStore.logout()
        uni.reLaunch({ url: '/pages/index/index' })
      }
    },
  })
}
</script>

<style lang="scss">
@import '@/uni.scss';

.my {
  background: $cf-bg;
  min-height: 100vh;
  position: relative;
}

.my__mesh {
  position: fixed; top: 0; left: 0; right: 0; height: 750rpx;
  background:
    radial-gradient(ellipse at 50% 0%,  rgba(45,139,87,0.30) 0%, transparent 50%),
    radial-gradient(ellipse at 10% 40%, rgba(46,134,193,0.18) 0%, transparent 45%),
    radial-gradient(ellipse at 90% 30%, rgba(123,79,160,0.14) 0%, transparent 40%);
  pointer-events: none; z-index: 0;
  animation: meshBreathe 7s ease-in-out infinite;
}

.my__statusbar { height: var(--status-bar-height, 44px); position: relative; z-index: 2; }
.my__scroll { position: relative; z-index: 1; }

// ─── Hero ─────────────────────────────────────────────────────────────────────
.my__hero {
  display: flex; flex-direction: column; align-items: center;
  padding: 16rpx 40rpx 48rpx;
  position: relative;
}

.my__edit-btn {
  position: absolute; top: 16rpx; right: 40rpx;
  width: 64rpx; height: 64rpx;
  background: $cf-glass-bg; border-radius: $r-full;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center;
  &:active { opacity: 0.7; }
}

// Avatar frame with animated ring
.my__avatar-frame {
  position: relative;
  width: 180rpx; height: 180rpx;
  margin-bottom: 28rpx;
  &:active { opacity: 0.9; }
}

.my__avatar-ring-outer {
  position: absolute; inset: -6rpx;
  border-radius: $r-full;
  background: conic-gradient(from 0deg, #2D8B57, #2E86C1, #7B4FA0, #B8D430, #2D8B57);
  animation: spin 4s linear infinite;
  opacity: 0.8;
}

.my__avatar-ring-inner {
  position: absolute; inset: -2rpx;
  border-radius: $r-full;
  background: $cf-bg;
}

.my__avatar {
  position: absolute; inset: 0;
  width: 180rpx; height: 180rpx;
  border-radius: $r-full;
  background: $cf-card-solid;
}

.my__avatar-tier-badge {
  position: absolute; bottom: 4rpx; right: 4rpx;
  width: 44rpx; height: 44rpx;
  border-radius: $r-full;
  display: flex; align-items: center; justify-content: center;
  border: 3rpx solid $cf-bg;
  z-index: 3;
}
.my__avatar-tier-text {
  font-size: 18rpx; font-weight: 900; color: #fff;
}

.my__name {
  font-size: 44rpx; font-weight: 900;
  color: $cf-white; letter-spacing: -0.02em;
  display: block; margin-bottom: 6rpx;
}

.my__handle {
  font-size: 22rpx; color: $cf-text-2;
  display: block; margin-bottom: 32rpx;
}

.my__login-cta {
  font-size: 26rpx; color: $cf-green; font-weight: 600;
  display: block; margin-bottom: 32rpx;
}

// ── Skill level bar ────────────────────────────────────────────────────────────
.my__skill-section {
  width: 100%; margin-bottom: 32rpx;
}

.my__skill-bar {
  display: flex; gap: 6rpx; margin-bottom: 12rpx;
}

.my__skill-pip {
  flex: 1; height: 8rpx; border-radius: $r-full;
  background: rgba(255,255,255,0.1);
  transition: background 0.3s;
  &--active { }
  &--current {
    box-shadow: 0 0 12rpx rgba(45,139,87,0.5);
  }
}

.my__skill-label-row {
  position: relative; display: flex;
  justify-content: space-between; align-items: center;
}
.my__skill-label-left, .my__skill-label-right {
  font-size: 18rpx; color: $cf-text-3;
}

.my__skill-current-label {
  position: absolute; transform: translateX(-50%);
  background: $cf-glass-bg; border: 0.5px solid $cf-glass-border;
  border-radius: $r-full; padding: 3rpx 14rpx;
  backdrop-filter: blur(8px);
}
.my__skill-current-text { font-size: 18rpx; color: $cf-white; font-weight: 700; }

// ── Stats glass card ────────────────────────────────────────────────────────────
.my__stats-glass {
  display: flex; align-items: stretch;
  width: 100%;
  background: $cf-glass-bg;
  border: 0.5px solid $cf-glass-border;
  border-radius: $r-xl;
  backdrop-filter: blur(16px);
  overflow: hidden;
  box-shadow: 0 4rpx 24rpx rgba(0,0,0,0.2);
}

.my__stat {
  flex: 1; position: relative;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 28rpx 16rpx;
  gap: 6rpx;
}

.my__stat-sep {
  position: absolute; right: 0; top: 20%;
  width: 0.5px; height: 60%; background: $cf-line;
}

.my__stat-value {
  font-size: 36rpx; font-weight: 900;
  color: $cf-white; letter-spacing: -0.02em;
}
.my__stat-label { font-size: 18rpx; color: $cf-text-2; }

// ─── Quick actions ─────────────────────────────────────────────────────────────
.my__section--actions {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 16rpx; margin: 0 32rpx 16rpx;
}

.my__action-card {
  display: flex; flex-direction: column; align-items: center; gap: 10rpx;
  position: relative;
  &:active { opacity: 0.8; }
}

.my__action-icon-ring {
  width: 96rpx; height: 96rpx;
  border-radius: $r-xl;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6rpx 20rpx rgba(0,0,0,0.25);
}

.my__action-label {
  font-size: 21rpx; color: $cf-text-2;
  font-weight: 500; text-align: center;
}

.my__action-badge {
  position: absolute; top: -4rpx; right: -4rpx;
  background: #D4652A;
  border-radius: $r-full; padding: 2rpx 10rpx;
  border: 2rpx solid $cf-bg;
}
.my__action-badge-text { font-size: 16rpx; font-weight: 700; color: #fff; }

// ─── Section cards ─────────────────────────────────────────────────────────────
.my__section-card {
  margin: 0 32rpx 16rpx;
  background: $cf-glass-bg;
  border-radius: $r-xl;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(16px);
  overflow: hidden;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.14);
}

.my__section-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 24rpx 28rpx 20rpx;
  border-bottom: 0.5px solid $cf-line;
}

.my__section-head-left { display: flex; align-items: center; gap: 12rpx; }

.my__section-head-dot {
  width: 8rpx; height: 8rpx; border-radius: $r-full;
  &--green { background: $cf-green; box-shadow: 0 0 8rpx rgba(45,139,87,0.7); }
  &--blue  { background: $cf-blue;  box-shadow: 0 0 8rpx rgba(46,134,193,0.7); }
  &--grey  { background: $cf-text-3; }
}

.my__section-head-title {
  font-size: 24rpx; font-weight: 700; color: $cf-white;
  letter-spacing: 0.01em;
}

.my__section-head-more {
  display: flex; align-items: center; gap: 4rpx;
  &:active { opacity: 0.7; }
}
.my__section-head-more-text {
  font-size: 22rpx; color: rgba(45,139,87,0.9); font-weight: 500;
}

// ─── Activity rows ─────────────────────────────────────────────────────────────
.my__activity-row {
  display: flex; align-items: center; gap: 16rpx;
  padding: 20rpx 28rpx;
  border-bottom: 0.5px solid $cf-line;
  &--last { border-bottom: none; }
  &:active { background: rgba(255,255,255,0.03); }
}

.my__activity-icon-wrap {
  width: 60rpx; height: 60rpx; border-radius: $r-md;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  &--court { background: rgba(45,139,87,0.15); border: 0.5px solid rgba(45,139,87,0.25); }
  &--coach { background: rgba(46,134,193,0.15); border: 0.5px solid rgba(46,134,193,0.25); }
}

.my__activity-info { flex: 1; }
.my__activity-venue { font-size: 25rpx; font-weight: 600; color: $cf-white; display: block; }
.my__activity-detail { font-size: 20rpx; color: $cf-text-2; margin-top: 4rpx; display: block; }

.my__activity-right {
  display: flex; flex-direction: column; align-items: flex-end; gap: 8rpx;
}

.my__activity-status {
  display: flex; align-items: center; gap: 6rpx;
  &--confirmed .my__activity-status-dot { background: $cf-success; }
  &--pending   .my__activity-status-dot { background: $cf-amber; animation: pulse 1.5s infinite; }
  &--cancelled .my__activity-status-dot { background: $cf-text-3; }
}
.my__activity-status-dot { width: 8rpx; height: 8rpx; border-radius: $r-full; }
.my__activity-status-text {
  font-size: 18rpx; font-weight: 600;
  .my__activity-status--confirmed & { color: $cf-success; }
  .my__activity-status--pending   & { color: $cf-amber; }
  .my__activity-status--cancelled & { color: $cf-text-3; }
}
.my__activity-price { font-size: 24rpx; font-weight: 700; color: $cf-white; }

.my__activity-empty {
  display: flex; flex-direction: column; align-items: center;
  padding: 60rpx 40rpx; gap: 16rpx;
}
.my__activity-empty-text { font-size: 26rpx; color: $cf-text-2; }
.my__activity-empty-btn {
  background: linear-gradient(135deg, $cf-green, $cf-blue);
  border-radius: $r-full; padding: 14rpx 48rpx;
  box-shadow: 0 4rpx 16rpx $cf-green-glow;
  &:active { opacity: 0.85; }
}
.my__activity-empty-btn-text { font-size: 24rpx; font-weight: 700; color: #fff; }

// ─── Tennis profile grid ───────────────────────────────────────────────────────
.my__tennis-grid {
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: 0;
}

.my__tennis-attr {
  display: flex; align-items: center; gap: 14rpx;
  padding: 20rpx 28rpx;
  border-bottom: 0.5px solid $cf-line;
  border-right: 0.5px solid $cf-line;
  &:nth-child(even) { border-right: none; }
  &:nth-last-child(-n+2) { border-bottom: none; }
}

.my__tennis-attr-icon {
  width: 52rpx; height: 52rpx; border-radius: $r-md;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.my__tennis-attr-label { font-size: 18rpx; color: $cf-text-2; display: block; flex: 1; }
.my__tennis-attr-value { font-size: 22rpx; font-weight: 700; color: $cf-white; flex-shrink: 0; }

// ─── Settings ─────────────────────────────────────────────────────────────────
.my__setting-row {
  display: flex; align-items: center; gap: 16rpx;
  padding: 20rpx 28rpx;
  border-bottom: 0.5px solid $cf-line;
  &--last { border-bottom: none; }
  &:active { background: rgba(255,255,255,0.03); }
}

.my__setting-icon-wrap {
  width: 52rpx; height: 52rpx; border-radius: $r-md;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.my__setting-label {
  flex: 1; font-size: 26rpx; color: $cf-white; font-weight: 500;
  &--danger { color: $cf-danger; }
}

.my__setting-right {
  display: flex; align-items: center; gap: 8rpx;
}
.my__setting-value { font-size: 22rpx; color: $cf-text-2; }

// ─── Brand footer ─────────────────────────────────────────────────────────────
.my__brand-footer {
  display: flex; flex-direction: column; align-items: center;
  padding: 40rpx 0 20rpx; gap: 8rpx;
}

.my__brand-name {
  font-size: 28rpx; font-weight: 900;
  background: linear-gradient(90deg, #4ade80, #60a5fa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.04em;
}

.my__brand-version {
  font-size: 18rpx; color: $cf-text-3;
}
</style>
