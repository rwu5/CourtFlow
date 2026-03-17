<template>
  <view class="vd">

    <!-- ── Hero gallery ─────────────────────────────────────────────────── -->
    <view class="vd__gallery">
      <swiper class="vd__swiper" :current="photoIndex" @change="e => photoIndex = e.detail.current" circular>
        <swiper-item v-for="(photo, i) in venue.photos" :key="i">
          <image class="vd__photo" :src="photo" mode="aspectFill" />
        </swiper-item>
      </swiper>
      <view class="vd__gallery-fade" />

      <!-- Back -->
      <view class="vd__back" @tap="goBack">
        <cf-icon name="chevron-left" :size="22" color="rgba(255,255,255,0.9)" />
      </view>

      <!-- Photo dots -->
      <view class="vd__photo-dots">
        <view
          v-for="(_, i) in venue.photos"
          :key="i"
          class="vd__photo-dot"
          :class="{ 'vd__photo-dot--active': photoIndex === i }"
        />
      </view>

      <!-- Floating name -->
      <view class="vd__hero-info">
        <view class="vd__hero-tags">
          <view class="vd__hero-tag vd__hero-tag--self" v-if="venue.isSelfOperated">
            <text>自营</text>
          </view>
          <view v-for="s in venue.surfaces" :key="s" class="vd__hero-tag vd__hero-tag--surface">
            <text>{{ s }}</text>
          </view>
          <view class="vd__hero-open-badge" :class="{ 'vd__hero-open-badge--closed': !isOpen }">
            <view class="vd__hero-open-dot" />
            <text class="vd__hero-open-text">{{ isOpen ? '营业中' : '已关门' }}</text>
          </view>
        </view>
        <text class="vd__hero-name">{{ venue.name }}</text>
        <view class="vd__hero-meta">
          <cf-icon name="location" :size="16" color="rgba(255,255,255,0.5)" />
          <text class="vd__hero-addr">{{ venue.address }}</text>
        </view>
      </view>
    </view>

    <!-- ── Section tab bar ──────────────────────────────────────────────── -->
    <view class="vd__tabs">
      <view
        v-for="tab in tabs"
        :key="tab.key"
        class="vd__tab"
        :class="{ 'vd__tab--active': activeTab === tab.key }"
        @tap="activeTab = tab.key"
      >
        <text class="vd__tab-label">{{ tab.label }}</text>
        <view v-if="activeTab === tab.key" class="vd__tab-line" />
      </view>
    </view>

    <!-- ── Tab content ──────────────────────────────────────────────────── -->
    <scroll-view class="vd__body" scroll-y>

      <!-- ════════ TAB: 预订 ════════ -->
      <view v-if="activeTab === 'book'">

        <!-- Court picker -->
        <view class="vd__block">
          <view class="vd__block-header">
            <text class="vd__block-title">选择场地</text>
            <text class="vd__block-sub">共 {{ venue.courts.length }} 块</text>
          </view>
          <scroll-view class="vd__court-scroll" scroll-x>
            <view class="vd__court-row">
              <view
                v-for="c in venue.courts"
                :key="c.id"
                class="vd__court-card"
                :class="{ 'vd__court-card--active': selectedCourt === c.id }"
                @tap="selectedCourt = c.id"
              >
                <view class="vd__court-avail-bar">
                  <view
                    class="vd__court-avail-fill"
                    :style="{ width: c.availPct + '%', background: c.availColor }"
                  />
                </view>
                <view class="vd__court-surface-tag" :style="{ background: c.surfaceColor + '22', borderColor: c.surfaceColor + '55' }">
                  <text class="vd__court-surface-text" :style="{ color: c.surfaceColor }">{{ c.surface }}</text>
                </view>
                <text class="vd__court-name">{{ c.name }}</text>
                <text class="vd__court-price">¥{{ c.pricePerHour }}<text class="vd__court-price-u">/时</text></text>
                <view class="vd__court-avail-label">
                  <view class="vd__court-avail-dot" :style="{ background: c.availColor }" />
                  <text class="vd__court-avail-text" :style="{ color: c.availColor }">{{ c.availLabel }}</text>
                </view>
                <!-- Active check -->
                <view v-if="selectedCourt === c.id" class="vd__court-check">
                  <cf-icon name="check" :size="14" color="#fff" />
                </view>
              </view>
            </view>
          </scroll-view>
        </view>

        <!-- Date picker -->
        <view class="vd__block">
          <scroll-view class="vd__date-scroll" scroll-x :scroll-into-view="'vdd-' + selectedDate">
            <view class="vd__date-row">
              <view
                v-for="d in dateTabs"
                :key="d.dateStr"
                :id="'vdd-' + d.dateStr"
                class="vd__date-chip"
                :class="{ 'vd__date-chip--active': selectedDate === d.dateStr }"
                @tap="selectedDate = d.dateStr"
              >
                <text class="vd__date-wd">{{ d.weekday }}</text>
                <text class="vd__date-num">{{ d.day }}</text>
                <view v-if="d.isToday" class="vd__date-today-dot" />
              </view>
            </view>
          </scroll-view>
        </view>

        <!-- Time slot grid -->
        <view class="vd__block">
          <view class="vd__block-header">
            <text class="vd__block-title">时段 & 价格</text>
            <view class="vd__legend-row">
              <view class="vd__legend-item">
                <view class="vd__legend-dot vd__legend-dot--avail" />
                <text class="vd__legend-text">可预订</text>
              </view>
              <view class="vd__legend-item">
                <view class="vd__legend-dot vd__legend-dot--selected" />
                <text class="vd__legend-text">已选</text>
              </view>
              <view class="vd__legend-item">
                <view class="vd__legend-dot vd__legend-dot--booked" />
                <text class="vd__legend-text">已订</text>
              </view>
            </view>
          </view>

          <view class="vd__slots-grid">
            <view
              v-for="slot in currentCourtSlots"
              :key="slot.time"
              class="vd__slot"
              :class="{
                'vd__slot--selected': selectedSlots.includes(slot.time),
                'vd__slot--booked':   slot.status === 'booked',
                'vd__slot--held':     slot.status === 'held',
                'vd__slot--unavail':  slot.status === 'unavail',
              }"
              @tap="toggleSlot(slot)"
            >
              <text class="vd__slot-time">{{ slot.time }}</text>
              <template v-if="slot.status === 'available'">
                <text class="vd__slot-price">¥{{ slot.price }}</text>
              </template>
              <template v-else-if="selectedSlots.includes(slot.time)">
                <cf-icon name="check" :size="14" color="#B8D430" />
              </template>
              <template v-else-if="slot.status === 'booked'">
                <text class="vd__slot-status-text">已订</text>
              </template>
              <template v-else-if="slot.status === 'held'">
                <cf-icon name="clock" :size="13" color="#FBBF24" />
              </template>
              <template v-else>
                <view class="vd__slot-dash" />
              </template>
            </view>
          </view>
        </view>

        <view style="height: 200rpx;" />
      </view>

      <!-- ════════ TAB: 教练 ════════ -->
      <view v-if="activeTab === 'coaches'">
        <view class="vd__block">
          <view class="vd__block-header">
            <text class="vd__block-title">驻场教练</text>
            <text class="vd__block-sub">{{ venue.coaches.length }} 位</text>
          </view>
          <view class="vd__coaches-list">
            <view
              v-for="c in venue.coaches"
              :key="c.id"
              class="vd__coach-row"
              @tap="goCoachProfile(c.id)"
            >
              <!-- Avatar -->
              <view class="vd__coach-av-wrap">
                <image class="vd__coach-av" :src="c.avatar" mode="aspectFill" />
                <view class="vd__coach-ring" :style="{ borderColor: c.color }" />
                <view class="vd__coach-online" :class="{ 'vd__coach-online--off': !c.isAvailable }" />
              </view>

              <!-- Info -->
              <view class="vd__coach-info">
                <view class="vd__coach-name-row">
                  <text class="vd__coach-name">{{ c.name }} 教练</text>
                  <view class="vd__coach-cert" :style="{ background: c.color + '20', borderColor: c.color + '45' }">
                    <text class="vd__coach-cert-text" :style="{ color: c.color }">{{ c.cert }}</text>
                  </view>
                </view>
                <view class="vd__coach-meta-row">
                  <view class="vd__coach-stars">
                    <cf-icon name="star" :size="14" color="#FBBF24" />
                    <text class="vd__coach-rating">{{ c.rating }}</text>
                  </view>
                  <text class="vd__coach-sessions">{{ c.sessions }}节课</text>
                  <view
                    v-for="ct in c.courtTypes"
                    :key="ct"
                    class="vd__coach-court-tag"
                  >
                    <text class="vd__coach-court-tag-text">{{ ct }}</text>
                  </view>
                </view>
                <text class="vd__coach-spec">{{ c.specialty }}</text>
              </view>

              <!-- Price + book -->
              <view class="vd__coach-right">
                <text class="vd__coach-price">¥{{ c.pricePerHour }}</text>
                <text class="vd__coach-price-u">/时</text>
                <view class="vd__coach-book-btn" @tap.stop="bookCoach(c.id)">
                  <text class="vd__coach-book-text">约课</text>
                </view>
              </view>
            </view>
          </view>
        </view>
        <view style="height: 40rpx;" />
      </view>

      <!-- ════════ TAB: 课程 ════════ -->
      <view v-if="activeTab === 'courses'">
        <view class="vd__block">
          <view class="vd__block-header">
            <text class="vd__block-title">场馆课程</text>
            <text class="vd__block-sub">{{ venue.courses.length }} 门</text>
          </view>
          <view class="vd__courses-list">
            <view
              v-for="course in venue.courses"
              :key="course.id"
              class="vd__course-card"
              @tap="goCourses"
            >
              <!-- Type bar -->
              <view class="vd__course-type-bar" :style="{ background: course.typeColor }" />

              <view class="vd__course-body">
                <!-- Top row -->
                <view class="vd__course-top">
                  <text class="vd__course-name">{{ course.name }}</text>
                  <view class="vd__course-type-badge" :style="{ background: course.typeColor + '20', borderColor: course.typeColor + '40' }">
                    <text class="vd__course-type-text" :style="{ color: course.typeColor }">{{ course.typeLabel }}</text>
                  </view>
                </view>

                <!-- Coach row -->
                <view class="vd__course-coach-row">
                  <image class="vd__course-coach-av" :src="course.coachAvatar" mode="aspectFill" />
                  <text class="vd__course-coach-name">{{ course.coachName }}</text>
                  <view class="vd__course-cert" :style="{ color: course.coachColor }">
                    <text>{{ course.coachCert }}</text>
                  </view>
                </view>

                <!-- Meta -->
                <view class="vd__course-meta">
                  <view class="vd__course-meta-item">
                    <cf-icon name="calendar" :size="14" color="rgba(255,255,255,0.4)" />
                    <text class="vd__course-meta-text">{{ course.schedule }}</text>
                  </view>
                  <view class="vd__course-meta-item">
                    <cf-icon name="clock" :size="14" color="rgba(255,255,255,0.4)" />
                    <text class="vd__course-meta-text">{{ course.duration }}</text>
                  </view>
                  <view class="vd__course-meta-item">
                    <cf-icon name="person" :size="14" color="rgba(255,255,255,0.4)" />
                    <text class="vd__course-meta-text vd__course-spots" :class="{ 'vd__course-spots--urgent': course.spotsLeft <= 2 }">
                      余 {{ course.spotsLeft }} 位
                    </text>
                  </view>
                </view>

                <!-- Bottom -->
                <view class="vd__course-bottom">
                  <text class="vd__course-price">¥{{ course.price }}<text class="vd__course-price-u">/节</text></text>
                  <view class="vd__course-join-btn">
                    <text class="vd__course-join-text">立即报名</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>
        <view style="height: 40rpx;" />
      </view>

      <!-- ════════ TAB: 信息 ════════ -->
      <view v-if="activeTab === 'info'">
        <!-- Location -->
        <view class="vd__block">
          <view class="vd__info-row" @tap="openMap">
            <view class="vd__info-icon-wrap vd__info-icon-wrap--green">
              <cf-icon name="location" :size="20" color="#2D8B57" />
            </view>
            <view class="vd__info-content">
              <text class="vd__info-label">地址</text>
              <text class="vd__info-value">{{ venue.address }}</text>
            </view>
            <view class="vd__info-action">
              <text class="vd__info-action-text">导航</text>
              <cf-icon name="chevron-right" :size="15" color="#2D8B57" />
            </view>
          </view>
          <view class="vd__divider" />
          <view class="vd__info-row">
            <view class="vd__info-icon-wrap vd__info-icon-wrap--blue">
              <cf-icon name="clock" :size="20" color="#2E86C1" />
            </view>
            <view class="vd__info-content">
              <text class="vd__info-label">营业时间</text>
              <text class="vd__info-value">{{ venue.openTime }} – {{ venue.closeTime }}</text>
            </view>
          </view>
        </view>

        <!-- Facilities -->
        <view class="vd__block">
          <text class="vd__block-title" style="margin-bottom: 20rpx;">场馆设施</text>
          <view class="vd__facilities-wrap">
            <view v-for="f in venue.facilities" :key="f.name" class="vd__facility-chip">
              <cf-icon :name="f.icon" :size="18" :color="f.color" />
              <text class="vd__facility-name">{{ f.name }}</text>
            </view>
          </view>
        </view>

        <!-- Contact -->
        <view class="vd__block">
          <text class="vd__block-title" style="margin-bottom: 20rpx;">联系场馆</text>
          <view class="vd__contact-row">
            <view class="vd__contact-btn" @tap="callPhone">
              <view class="vd__contact-icon-wrap vd__contact-icon-wrap--green">
                <cf-icon name="phone" :size="22" color="#2D8B57" />
              </view>
              <text class="vd__contact-label">电话联系</text>
              <text class="vd__contact-value">{{ venue.phone }}</text>
            </view>
            <view class="vd__contact-btn" @tap="openWeChat">
              <view class="vd__contact-icon-wrap vd__contact-icon-wrap--violet">
                <cf-icon name="chat" :size="22" color="#7B4FA0" />
              </view>
              <text class="vd__contact-label">微信客服</text>
              <text class="vd__contact-value">在线咨询</text>
            </view>
          </view>
        </view>

        <view style="height: 40rpx;" />
      </view>

    </scroll-view>

    <!-- ── Booking footer (only on 预订 tab) ───────────────────────────── -->
    <view class="vd__footer" :class="{ 'vd__footer--visible': activeTab === 'book' }">
      <view class="vd__footer-inner">
        <view v-if="selectedSlots.length === 0" class="vd__footer-idle">
          <text class="vd__footer-idle-label">{{ currentCourt?.name }}</text>
          <text class="vd__footer-price-from">¥{{ currentCourt?.pricePerHour }}<text class="vd__footer-price-u">/时</text></text>
        </view>
        <view v-else class="vd__footer-selected">
          <view class="vd__footer-selected-info">
            <text class="vd__footer-slots-count">已选 {{ selectedSlots.length }} 个时段</text>
            <text class="vd__footer-total">¥{{ selectedTotal }}</text>
          </view>
        </view>
        <view class="vd__footer-btn" :class="{ 'vd__footer-btn--dim': selectedSlots.length === 0 }" @tap="goOrder">
          <text class="vd__footer-btn-text">{{ selectedSlots.length > 0 ? '去下单' : '选择时段' }}</text>
          <cf-icon name="chevron-right" :size="18" color="#fff" />
        </view>
      </view>
    </view>

  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'

// ── State ──────────────────────────────────────────────────────────────────────
const photoIndex   = ref(0)
const activeTab    = ref('book')
const selectedCourt = ref('court1')
const selectedDate  = ref('')
const selectedSlots = ref<string[]>([])

const tabs = [
  { key: 'book',    label: '预订' },
  { key: 'coaches', label: '教练' },
  { key: 'courses', label: '课程' },
  { key: 'info',    label: '信息' },
]

// ── Venue data ─────────────────────────────────────────────────────────────────
const venue = ref({
  id: '1',
  name: '卓越网球中心',
  address: '朝阳区建国路89号卓越世纪中心B座',
  openTime: '07:00',
  closeTime: '22:00',
  priceFrom: 80,
  isSelfOperated: true,
  phone: '010-12345678',
  photos: [
    '/static/venue-placeholder.jpg',
    '/static/venue-placeholder.jpg',
    '/static/venue-placeholder.jpg',
  ],
  surfaces: ['硬地', '红土'],
  courts: [
    { id: 'court1', name: '硬地1号', surface: '硬地', surfaceColor: '#2E86C1', pricePerHour: 80,  availPct: 75, availLabel: '多空位', availColor: '#34d399' },
    { id: 'court2', name: '硬地2号', surface: '硬地', surfaceColor: '#2E86C1', pricePerHour: 80,  availPct: 30, availLabel: '少量', availColor: '#FBBF24' },
    { id: 'court3', name: '红土1号', surface: '红土', surfaceColor: '#D4652A', pricePerHour: 120, availPct: 60, availLabel: '可预订', availColor: '#34d399' },
    { id: 'court4', name: '红土2号', surface: '红土', surfaceColor: '#D4652A', pricePerHour: 120, availPct: 0,  availLabel: '已满',   availColor: '#F04545' },
    { id: 'court5', name: '室内硬地', surface: '室内', surfaceColor: '#7B4FA0', pricePerHour: 150, availPct: 50, availLabel: '可预订', availColor: '#34d399' },
  ],
  facilities: [
    { icon: 'location', color: '#2E86C1', name: '停车场' },
    { icon: 'shield',   color: '#34d399', name: '淋浴室' },
    { icon: 'person',   color: '#7B4FA0', name: '更衣室' },
    { icon: 'ticket',   color: '#D4652A', name: '装备租赁' },
    { icon: 'star',     color: '#FBBF24', name: '夜间照明' },
    { icon: 'building', color: '#2D8B57', name: '空调场馆' },
  ],
  coaches: [
    {
      id: 'c1', name: '张明', cert: 'ITF L2', avatar: '/static/coach-placeholder.jpg',
      color: '#2D8B57', pricePerHour: 300, isAvailable: true,
      rating: 4.9, sessions: 312, specialty: '正反手技术 · 发球提升',
      courtTypes: ['硬地', '红土'],
    },
    {
      id: 'c2', name: '陈刚', cert: 'ITF L2', avatar: '/static/coach-placeholder.jpg',
      color: '#D4652A', pricePerHour: 350, isAvailable: true,
      rating: 4.8, sessions: 180, specialty: '竞技提升 · 步伐训练',
      courtTypes: ['硬地'],
    },
    {
      id: 'c3', name: '王芳', cert: 'ITF L1', avatar: '/static/coach-placeholder.jpg',
      color: '#7B4FA0', pricePerHour: 250, isAvailable: false,
      rating: 4.7, sessions: 95, specialty: '青少年培训 · 基础入门',
      courtTypes: ['红土', '室内'],
    },
  ],
  courses: [
    {
      id: 'cs1', name: '周末精英私教课', typeLabel: '私教', typeColor: '#2D8B57',
      coachName: '张明', coachCert: 'ITF L2', coachAvatar: '/static/coach-placeholder.jpg', coachColor: '#2D8B57',
      schedule: '周六 09:00', duration: '90分钟', spotsLeft: 1, price: 380,
    },
    {
      id: 'cs2', name: '网球零基础启蒙班', typeLabel: '团体', typeColor: '#2E86C1',
      coachName: '王芳', coachCert: 'ITF L1', coachAvatar: '/static/coach-placeholder.jpg', coachColor: '#7B4FA0',
      schedule: '周二 / 周四 19:00', duration: '60分钟', spotsLeft: 4, price: 180,
    },
    {
      id: 'cs3', name: '夏季训练营', typeLabel: '训练营', typeColor: '#D4652A',
      coachName: '陈刚', coachCert: 'ITF L2', coachAvatar: '/static/coach-placeholder.jpg', coachColor: '#D4652A',
      schedule: '每日 08:00', duration: '3小时', spotsLeft: 6, price: 580,
    },
  ],
})

// ── Computed ───────────────────────────────────────────────────────────────────
const isOpen = computed(() => {
  const h = new Date().getHours()
  const [oh] = venue.value.openTime.split(':').map(Number)
  const [ch] = venue.value.closeTime.split(':').map(Number)
  return h >= oh && h < ch
})

const currentCourt = computed(() =>
  venue.value.courts.find(c => c.id === selectedCourt.value)
)

// Build 7-day date tabs
const dateTabs = computed(() => {
  const days = ['日', '一', '二', '三', '四', '五', '六']
  const now = new Date()
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(now)
    d.setDate(now.getDate() + i)
    return {
      dateStr: d.toISOString().slice(0, 10),
      weekday: i === 0 ? '今天' : '周' + days[d.getDay()],
      day: d.getDate(),
      isToday: i === 0,
    }
  })
})

// Generate hourly slots 07:00 – 21:00
const slotStatuses: Record<string, Record<string, Record<string, string>>> = {}
function getSlotStatus(courtId: string, date: string, time: string): { status: string; price: number } {
  const seed = (courtId + date + time).split('').reduce((a, c) => a + c.charCodeAt(0), 0)
  const r = seed % 10
  const court = venue.value.courts.find(c => c.id === courtId)
  if (r < 3) return { status: 'booked', price: court?.pricePerHour ?? 80 }
  if (r === 3) return { status: 'held', price: court?.pricePerHour ?? 80 }
  return { status: 'available', price: court?.pricePerHour ?? 80 }
}

const currentCourtSlots = computed(() => {
  const slots = []
  for (let h = 7; h <= 21; h++) {
    const time = (h < 10 ? '0' : '') + h + ':00'
    const { status, price } = getSlotStatus(selectedCourt.value, selectedDate.value, time)
    slots.push({ time, status, price })
  }
  return slots
})

const selectedTotal = computed(() => {
  const price = currentCourt.value?.pricePerHour ?? 80
  return selectedSlots.value.length * price
})

// ── Init ───────────────────────────────────────────────────────────────────────
onMounted(() => {
  selectedDate.value = dateTabs.value[0].dateStr
})

// ── Actions ────────────────────────────────────────────────────────────────────
function toggleSlot(slot: { time: string; status: string }) {
  if (slot.status === 'booked' || slot.status === 'held' || slot.status === 'unavail') return
  const idx = selectedSlots.value.indexOf(slot.time)
  if (idx >= 0) selectedSlots.value.splice(idx, 1)
  else selectedSlots.value.push(slot.time)
}

function goBack() { uni.navigateBack() }

function openMap() {
  uni.openLocation({ latitude: 39.9042, longitude: 116.4074, name: venue.value.name, address: venue.value.address })
}

function callPhone() { uni.makePhoneCall({ phoneNumber: venue.value.phone }) }

function openWeChat() { uni.showToast({ title: '微信客服暂未开放', icon: 'none' }) }

function goCoachProfile(id: string) {
  uni.navigateTo({ url: `/packages/coach/profile/index?id=${id}` })
}

function bookCoach(id: string) {
  uni.navigateTo({ url: `/packages/coach/profile/index?id=${id}` })
}

function goCourses() { uni.switchTab({ url: '/pages/courses/index' }) }

function goOrder() {
  if (selectedSlots.value.length === 0) return
  uni.navigateTo({
    url: `/packages/booking/order/index?venueId=${venue.value.id}&courtId=${selectedCourt.value}&date=${selectedDate.value}`,
  })
}
</script>

<style lang="scss">
@import '@/uni.scss';

// ── Root ──────────────────────────────────────────────────────────────────────
.vd {
  background: $cf-bg;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

// ── Gallery ───────────────────────────────────────────────────────────────────
.vd__gallery {
  position: relative;
  height: 520rpx;
  flex-shrink: 0;
}
.vd__swiper { width: 100%; height: 100%; }
.vd__photo  { width: 100%; height: 100%; }

.vd__gallery-fade {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(8,14,11,0.15) 0%,
    transparent 35%,
    rgba(8,14,11,0.6) 70%,
    $cf-bg 100%
  );
  pointer-events: none;
}

.vd__back {
  position: absolute;
  top: calc(var(--status-bar-height, 44px) + 16rpx);
  left: 32rpx;
  width: 72rpx; height: 72rpx;
  background: rgba(8,14,11,0.65);
  backdrop-filter: blur(12px);
  border-radius: $r-full;
  display: flex; align-items: center; justify-content: center;
  border: 0.5px solid $cf-glass-border-2;
}

.vd__photo-dots {
  position: absolute;
  bottom: 140rpx;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8rpx;
}
.vd__photo-dot {
  width: 8rpx; height: 8rpx;
  border-radius: $r-full;
  background: rgba(255,255,255,0.3);
  &--active { background: $cf-white; width: 20rpx; }
  transition: all 0.2s;
}

.vd__hero-info {
  position: absolute;
  bottom: 20rpx; left: 32rpx; right: 32rpx;
}
.vd__hero-tags {
  display: flex; flex-wrap: wrap; gap: 8rpx;
  margin-bottom: 10rpx;
}
.vd__hero-tag {
  padding: 4rpx 14rpx; border-radius: $r-full; font-size: 18rpx; font-weight: 700;
  &--self    { background: $cf-lime; color: #0a1a0d; }
  &--surface { background: rgba(0,0,0,0.45); color: $cf-white; border: 0.5px solid $cf-glass-border-2; backdrop-filter: blur(4px); }
}
.vd__hero-open-badge {
  display: flex; align-items: center; gap: 6rpx;
  padding: 4rpx 14rpx; border-radius: $r-full;
  background: rgba(52,211,153,0.14); border: 0.5px solid rgba(52,211,153,0.3);
  &--closed { background: rgba(240,69,69,0.12); border-color: rgba(240,69,69,0.25); }
}
.vd__hero-open-dot {
  width: 10rpx; height: 10rpx; border-radius: $r-full; background: $cf-success;
  .vd__hero-open-badge--closed & { background: $cf-danger; }
}
.vd__hero-open-text {
  font-size: 18rpx; font-weight: 600; color: $cf-success;
  .vd__hero-open-badge--closed & { color: $cf-danger; }
}
.vd__hero-name {
  display: block;
  font-size: 44rpx; font-weight: 800; color: $cf-white;
  letter-spacing: -0.02em;
  text-shadow: 0 2rpx 20rpx rgba(0,0,0,0.6);
  margin-bottom: 8rpx;
}
.vd__hero-meta {
  display: flex; align-items: center; gap: 6rpx;
}
.vd__hero-addr {
  font-size: 20rpx; color: rgba(255,255,255,0.55);
  flex: 1; overflow: hidden;
}

// ── Tabs ──────────────────────────────────────────────────────────────────────
.vd__tabs {
  display: flex;
  background: $cf-surface;
  border-bottom: 0.5px solid $cf-line;
  position: sticky;
  top: 0;
  z-index: 10;
}
.vd__tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24rpx 0 16rpx;
  position: relative;
  &:active { opacity: 0.75; }
}
.vd__tab-label {
  font-size: 26rpx;
  font-weight: 500;
  color: $cf-text-2;
  .vd__tab--active & { color: $cf-white; font-weight: 700; }
}
.vd__tab-line {
  position: absolute;
  bottom: 0; left: 20%; right: 20%;
  height: 3rpx;
  border-radius: $r-full;
  background: linear-gradient(90deg, $cf-green, $cf-lime);
}

// ── Body ──────────────────────────────────────────────────────────────────────
.vd__body {
  flex: 1;
  background: $cf-bg;
}

// ── Block (shared section card) ───────────────────────────────────────────────
.vd__block {
  margin: 24rpx 28rpx 0;
  background: $cf-glass-bg;
  border-radius: $r-xl;
  padding: 28rpx;
  border: 0.5px solid $cf-glass-border;
  backdrop-filter: blur(16px);
}
.vd__block-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}
.vd__block-title {
  font-size: 26rpx; font-weight: 700; color: $cf-white;
  letter-spacing: 0.01em;
  display: block;
}
.vd__block-sub {
  font-size: 20rpx; color: $cf-text-2;
}

// ── Court picker ──────────────────────────────────────────────────────────────
.vd__court-scroll { width: 100%; }
.vd__court-row { display: flex; gap: 16rpx; padding-bottom: 4rpx; }

.vd__court-card {
  flex-shrink: 0;
  width: 200rpx;
  background: rgba(255,255,255,0.04);
  border-radius: $r-xl;
  padding: 20rpx 18rpx;
  border: 1rpx solid $cf-line;
  display: flex; flex-direction: column; gap: 10rpx;
  position: relative;
  transition: border-color 0.2s;
  &--active {
    border-color: $cf-lime;
    background: rgba(184,212,48,0.06);
    box-shadow: 0 0 0 1rpx rgba(184,212,48,0.2), inset 0 0 20rpx rgba(184,212,48,0.04);
  }
  &:active { opacity: 0.85; }
}

.vd__court-avail-bar {
  height: 4rpx;
  background: rgba(255,255,255,0.08);
  border-radius: $r-full;
  overflow: hidden;
}
.vd__court-avail-fill {
  height: 100%;
  border-radius: $r-full;
  transition: width 0.3s;
}

.vd__court-surface-tag {
  align-self: flex-start;
  padding: 3rpx 12rpx;
  border-radius: $r-full;
  border: 0.5px solid;
}
.vd__court-surface-text {
  font-size: 18rpx; font-weight: 700;
}

.vd__court-name {
  font-size: 26rpx; font-weight: 700; color: $cf-white;
  display: block;
}
.vd__court-price {
  font-size: 28rpx; font-weight: 800; color: $cf-lime;
  display: block;
}
.vd__court-price-u {
  font-size: 18rpx; font-weight: 400; color: $cf-text-2;
}
.vd__court-avail-label {
  display: flex; align-items: center; gap: 6rpx;
}
.vd__court-avail-dot {
  width: 10rpx; height: 10rpx; border-radius: $r-full;
}
.vd__court-avail-text {
  font-size: 18rpx; font-weight: 600;
}

.vd__court-check {
  position: absolute;
  top: 14rpx; right: 14rpx;
  width: 36rpx; height: 36rpx;
  background: $cf-lime;
  border-radius: $r-full;
  display: flex; align-items: center; justify-content: center;
}

// ── Date picker ───────────────────────────────────────────────────────────────
.vd__date-scroll { width: 100%; }
.vd__date-row    { display: flex; gap: 12rpx; }

.vd__date-chip {
  flex-shrink: 0;
  width: 80rpx;
  background: rgba(255,255,255,0.04);
  border-radius: $r-lg;
  padding: 16rpx 0;
  display: flex; flex-direction: column; align-items: center; gap: 6rpx;
  border: 1rpx solid $cf-line;
  position: relative;
  &--active {
    background: rgba(184,212,48,0.10);
    border-color: $cf-lime;
  }
  &:active { opacity: 0.8; }
}
.vd__date-wd {
  font-size: 18rpx; color: $cf-text-2;
  .vd__date-chip--active & { color: $cf-lime; font-weight: 600; }
}
.vd__date-num {
  font-size: 30rpx; font-weight: 700; color: $cf-white;
  .vd__date-chip--active & { color: $cf-lime; }
}
.vd__date-today-dot {
  width: 8rpx; height: 8rpx;
  background: $cf-lime;
  border-radius: $r-full;
}

// ── Legend ────────────────────────────────────────────────────────────────────
.vd__legend-row {
  display: flex; gap: 16rpx; align-items: center;
}
.vd__legend-item {
  display: flex; align-items: center; gap: 6rpx;
}
.vd__legend-dot {
  width: 12rpx; height: 12rpx; border-radius: 3rpx;
  &--avail    { background: rgba(45,139,87,0.5); border: 1rpx solid rgba(45,139,87,0.7); }
  &--selected { background: $cf-lime; }
  &--booked   { background: rgba(255,255,255,0.12); border: 1rpx solid $cf-line; }
}
.vd__legend-text {
  font-size: 18rpx; color: $cf-text-2;
}

// ── Time slot grid ────────────────────────────────────────────────────────────
.vd__slots-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10rpx;
}

.vd__slot {
  background: rgba(45,139,87,0.08);
  border-radius: $r-md;
  padding: 14rpx 0;
  display: flex; flex-direction: column; align-items: center; gap: 6rpx;
  border: 1rpx solid rgba(45,139,87,0.18);
  min-height: 86rpx;
  transition: all 0.15s;
  &:active { opacity: 0.7; }

  &--selected {
    background: rgba(184,212,48,0.14);
    border-color: $cf-lime;
    box-shadow: 0 0 12rpx rgba(184,212,48,0.25), inset 0 0 8rpx rgba(184,212,48,0.06);
  }
  &--booked {
    background: rgba(255,255,255,0.025);
    border-color: rgba(255,255,255,0.06);
  }
  &--held {
    background: rgba(251,191,36,0.08);
    border-color: rgba(251,191,36,0.25);
  }
  &--unavail {
    background: transparent;
    border-color: transparent;
    opacity: 0.3;
  }
}
.vd__slot-time {
  font-size: 19rpx; font-weight: 600; color: $cf-text-2;
  .vd__slot--selected & { color: $cf-lime; }
  .vd__slot--booked &   { color: $cf-text-3; }
}
.vd__slot-price {
  font-size: 22rpx; font-weight: 800; color: $cf-white;
  .vd__slot--selected & { color: $cf-lime; }
}
.vd__slot-status-text {
  font-size: 18rpx; color: $cf-text-3;
}
.vd__slot-dash {
  width: 20rpx; height: 2rpx; background: $cf-line; border-radius: 1rpx;
}

// ── Coaches list ──────────────────────────────────────────────────────────────
.vd__coaches-list {
  display: flex; flex-direction: column; gap: 20rpx;
}
.vd__coach-row {
  display: flex; align-items: center; gap: 20rpx;
  padding: 20rpx;
  background: rgba(255,255,255,0.03);
  border-radius: $r-lg;
  border: 0.5px solid $cf-glass-border;
  &:active { opacity: 0.8; }
}

.vd__coach-av-wrap {
  position: relative; width: 100rpx; height: 100rpx; flex-shrink: 0;
}
.vd__coach-av {
  width: 100rpx; height: 100rpx; border-radius: $r-full; background: $cf-card-solid;
}
.vd__coach-ring {
  position: absolute; inset: -3rpx; border-radius: $r-full; border: 2.5rpx solid;
}
.vd__coach-online {
  position: absolute; bottom: 3rpx; right: 3rpx;
  width: 18rpx; height: 18rpx; border-radius: $r-full;
  background: $cf-success; border: 2rpx solid $cf-bg;
  &--off { background: $cf-text-3; }
}

.vd__coach-info { flex: 1; min-width: 0; }
.vd__coach-name-row {
  display: flex; align-items: center; gap: 10rpx; margin-bottom: 8rpx;
}
.vd__coach-name {
  font-size: 28rpx; font-weight: 700; color: $cf-white;
}
.vd__coach-cert {
  padding: 3rpx 12rpx; border-radius: $r-full; border: 0.5px solid;
}
.vd__coach-cert-text { font-size: 17rpx; font-weight: 700; }

.vd__coach-meta-row {
  display: flex; align-items: center; gap: 12rpx; margin-bottom: 8rpx; flex-wrap: wrap;
}
.vd__coach-stars { display: flex; align-items: center; gap: 4rpx; }
.vd__coach-rating { font-size: 20rpx; font-weight: 700; color: $cf-amber; }
.vd__coach-sessions { font-size: 20rpx; color: $cf-text-2; }
.vd__coach-court-tag {
  background: rgba(184,212,48,0.10); border: 0.5px solid rgba(184,212,48,0.25);
  border-radius: $r-full; padding: 2rpx 10rpx;
}
.vd__coach-court-tag-text { font-size: 17rpx; color: $cf-lime; font-weight: 600; }
.vd__coach-spec { font-size: 20rpx; color: $cf-text-2; }

.vd__coach-right {
  display: flex; flex-direction: column; align-items: center; gap: 8rpx; flex-shrink: 0;
}
.vd__coach-price {
  font-size: 32rpx; font-weight: 900; color: $cf-lime;
}
.vd__coach-price-u { font-size: 18rpx; color: $cf-text-2; }
.vd__coach-book-btn {
  background: linear-gradient(135deg, $cf-green, $cf-blue);
  border-radius: $r-full; padding: 10rpx 24rpx;
  &:active { opacity: 0.85; }
}
.vd__coach-book-text {
  font-size: 22rpx; font-weight: 700; color: #fff;
}

// ── Courses list ──────────────────────────────────────────────────────────────
.vd__courses-list { display: flex; flex-direction: column; gap: 16rpx; }

.vd__course-card {
  display: flex; border-radius: $r-lg; overflow: hidden;
  background: rgba(255,255,255,0.03);
  border: 0.5px solid $cf-glass-border;
  &:active { opacity: 0.8; }
}
.vd__course-type-bar { width: 6rpx; flex-shrink: 0; }
.vd__course-body { flex: 1; padding: 20rpx 20rpx 20rpx 16rpx; }

.vd__course-top {
  display: flex; align-items: center; gap: 12rpx; margin-bottom: 12rpx;
}
.vd__course-name {
  flex: 1; font-size: 26rpx; font-weight: 700; color: $cf-white;
}
.vd__course-type-badge {
  padding: 3rpx 12rpx; border-radius: $r-full; border: 0.5px solid; flex-shrink: 0;
}
.vd__course-type-text { font-size: 17rpx; font-weight: 700; }

.vd__course-coach-row {
  display: flex; align-items: center; gap: 10rpx; margin-bottom: 12rpx;
}
.vd__course-coach-av {
  width: 40rpx; height: 40rpx; border-radius: $r-full; background: $cf-card-solid;
}
.vd__course-coach-name { font-size: 22rpx; color: $cf-text-2; }
.vd__course-cert { font-size: 18rpx; font-weight: 700; }

.vd__course-meta {
  display: flex; gap: 16rpx; margin-bottom: 14rpx; flex-wrap: wrap;
}
.vd__course-meta-item { display: flex; align-items: center; gap: 5rpx; }
.vd__course-meta-text { font-size: 19rpx; color: $cf-text-2; }
.vd__course-spots {
  &--urgent { color: $cf-danger !important; font-weight: 700; }
}

.vd__course-bottom {
  display: flex; align-items: center; justify-content: space-between;
}
.vd__course-price {
  font-size: 32rpx; font-weight: 900; color: $cf-lime;
}
.vd__course-price-u { font-size: 18rpx; color: $cf-text-2; font-weight: 400; }
.vd__course-join-btn {
  background: linear-gradient(135deg, $cf-green, $cf-blue);
  border-radius: $r-full; padding: 10rpx 28rpx;
  &:active { opacity: 0.85; }
}
.vd__course-join-text { font-size: 22rpx; font-weight: 700; color: #fff; }

// ── Info tab ──────────────────────────────────────────────────────────────────
.vd__info-row { display: flex; align-items: center; gap: 20rpx; }
.vd__divider { height: 0.5px; background: $cf-line; margin: 20rpx 0; }
.vd__info-icon-wrap {
  width: 64rpx; height: 64rpx; border-radius: $r-md;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  &--green { background: rgba(45,139,87,0.12); }
  &--blue  { background: rgba(46,134,193,0.12); }
}
.vd__info-content { flex: 1; }
.vd__info-label { font-size: 20rpx; color: $cf-text-2; display: block; }
.vd__info-value { font-size: 26rpx; color: $cf-white; font-weight: 500; margin-top: 4rpx; display: block; }
.vd__info-action {
  display: flex; align-items: center; gap: 4rpx; flex-shrink: 0;
}
.vd__info-action-text { font-size: 22rpx; color: $cf-green; font-weight: 500; }

.vd__facilities-wrap { display: flex; flex-wrap: wrap; gap: 16rpx; }
.vd__facility-chip {
  display: flex; align-items: center; gap: 8rpx;
  background: rgba(255,255,255,0.04);
  border-radius: $r-md; padding: 12rpx 20rpx;
  border: 0.5px solid $cf-line;
}
.vd__facility-name { font-size: 22rpx; color: $cf-text-2; font-weight: 500; }

.vd__contact-row { display: flex; gap: 16rpx; }
.vd__contact-btn {
  flex: 1;
  background: rgba(255,255,255,0.03);
  border-radius: $r-lg; padding: 24rpx 16rpx;
  display: flex; flex-direction: column; align-items: center; gap: 10rpx;
  border: 0.5px solid $cf-glass-border;
  &:active { opacity: 0.8; }
}
.vd__contact-icon-wrap {
  width: 72rpx; height: 72rpx; border-radius: $r-full;
  display: flex; align-items: center; justify-content: center;
  &--green  { background: rgba(45,139,87,0.12); }
  &--violet { background: rgba(123,79,160,0.12); }
}
.vd__contact-label { font-size: 22rpx; color: $cf-text-2; font-weight: 600; }
.vd__contact-value { font-size: 20rpx; color: $cf-text-3; }

// ── Footer ────────────────────────────────────────────────────────────────────
.vd__footer {
  position: fixed;
  bottom: -200rpx;
  left: 0; right: 0;
  background: rgba(8,14,11,0.92);
  backdrop-filter: blur(24px) saturate(1.4);
  border-top: 0.5px solid $cf-glass-border-2;
  padding-bottom: env(safe-area-inset-bottom);
  transition: bottom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 100;
  &--visible { bottom: 0; }
}
.vd__footer-inner {
  display: flex; align-items: center;
  padding: 20rpx 32rpx; gap: 20rpx;
}
.vd__footer-idle {
  flex: 1; display: flex; flex-direction: column; gap: 4rpx;
}
.vd__footer-idle-label { font-size: 20rpx; color: $cf-text-2; }
.vd__footer-price-from { font-size: 36rpx; font-weight: 900; color: $cf-lime; }
.vd__footer-price-u { font-size: 18rpx; font-weight: 400; color: $cf-text-2; }

.vd__footer-selected { flex: 1; }
.vd__footer-selected-info { display: flex; flex-direction: column; gap: 4rpx; }
.vd__footer-slots-count { font-size: 20rpx; color: $cf-text-2; }
.vd__footer-total { font-size: 36rpx; font-weight: 900; color: $cf-lime; }

.vd__footer-btn {
  display: flex; align-items: center; gap: 6rpx;
  background: linear-gradient(135deg, $cf-green, $cf-blue);
  border-radius: $r-full; padding: 0 32rpx;
  height: 88rpx;
  box-shadow: 0 6rpx 24rpx $cf-green-glow;
  &--dim {
    background: rgba(255,255,255,0.08);
    box-shadow: none;
  }
  &:active { opacity: 0.85; }
}
.vd__footer-btn-text {
  font-size: 28rpx; font-weight: 700; color: #fff;
  letter-spacing: 0.02em;
}
</style>
