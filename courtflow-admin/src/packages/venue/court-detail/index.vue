<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">{{ court?.name || '场地详情' }}</text>
      <view class="page-header__action" @click="goSettings">
        <CfIcon name="settings" :size="20" color="rgba(255,255,255,0.6)" />
      </view>
    </view>

    <scroll-view scroll-y class="content">
      <!-- Court info -->
      <view v-if="court" class="info-card cf-glass-card">
        <view class="info-row">
          <text class="info-label">场地类型</text>
          <text class="info-value">{{ court.surface ? surfaceLabel(court.surface) : '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">场地环境</text>
          <text class="info-value">{{ court.is_indoor ? '室内' : '室外' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">时段时长</text>
          <text class="info-value">{{ court.slot_duration_minutes }} 分钟</text>
        </view>
        <view class="info-row">
          <text class="info-label">状态</text>
          <view :class="['cf-badge', court.is_active ? 'cf-badge--green' : 'cf-badge--grey']">
            {{ court.is_active ? '启用' : '停用' }}
          </view>
        </view>
      </view>

      <!-- Photos -->
      <view class="section">
        <view class="section__header">
          <text class="section__title">场地照片</text>
          <CfButton type="ghost" size="sm" icon="plus" @click="goPhotos">管理</CfButton>
        </view>
        <CfEmpty v-if="!photos.length" icon="image" text="暂无照片" />
        <scroll-view v-else scroll-x class="photo-strip">
          <view class="photo-strip__inner">
            <image
              v-for="m in photos"
              :key="m.id"
              :src="m.url"
              class="photo-strip__img"
              mode="aspectFill"
              @click="previewPhoto(m.url)"
            />
          </view>
        </scroll-view>
      </view>

      <!-- Pricing rules -->
      <view class="section">
        <view class="section__header">
          <text class="section__title">定价规则</text>
          <CfButton type="ghost" size="sm" icon="plus" @click="goCreateRule">新建</CfButton>
        </view>
        <CfEmpty v-if="!rules.length" icon="money" text="暂无定价规则" />
        <view
          v-for="rule in rules"
          :key="rule.id"
          class="rule-card cf-glass-card"
          @click="goEditRule(rule.id)"
        >
          <view class="rule-card__top">
            <text class="rule-card__name">{{ rule.name }}</text>
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
      </view>

      <!-- Court blocks -->
      <view class="section">
        <view class="section__header">
          <text class="section__title">维护窗口</text>
          <CfButton type="ghost" size="sm" icon="plus" @click="showBlockModal = true">新建</CfButton>
        </view>
        <CfEmpty v-if="!blocks.length" icon="clock" text="暂无维护安排" />
        <view
          v-for="block in blocks"
          :key="block.id"
          class="block-card cf-glass-card"
        >
          <view class="block-card__top">
            <text class="block-card__time">{{ formatBlockRange(block.start_at, block.end_at) }}</text>
            <view class="block-card__del" @click="deleteBlock(block.id)">
              <CfIcon name="trash" :size="16" color="rgba(255,255,255,0.4)" />
            </view>
          </view>
          <text v-if="block.reason" class="block-card__reason">{{ block.reason }}</text>
        </view>
      </view>

      <!-- Recent bookings -->
      <view class="section">
        <view class="section__header">
          <text class="section__title">近期预约</text>
          <CfButton type="ghost" size="sm" @click="goBookingList">查看全部</CfButton>
        </view>
        <CfEmpty v-if="!recentBookings.length" icon="document" text="暂无预约" />
        <view
          v-for="r in recentBookings"
          :key="r.id"
          class="booking-card cf-glass-card"
          @click="goBookingDetail(r.id)"
        >
          <view class="booking-card__top">
            <text class="booking-card__time">{{ formatSlot(r.slot_start_at, r.slot_end_at) }}</text>
            <view :class="['cf-badge', bookingBadge(r.status)]">
              {{ bookingStatusLabel(r.status) }}
            </view>
          </view>
          <view class="booking-card__bottom">
            <text class="booking-card__user">{{ r.user_nickname || r.user_phone || '未知用户' }}</text>
            <text class="booking-card__price">&yen;{{ (r.amount_cents / 100).toFixed(0) }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- Block creation modal -->
    <CfModal
      :visible="showBlockModal"
      title="新建维护窗口"
      confirm-text="创建"
      @close="showBlockModal = false"
      @confirm="createBlock"
    >
      <view class="block-form">
        <CfFormItem label="开始时间" required>
          <picker mode="date" :value="blockForm.startDate" @change="blockForm.startDate = $event.detail.value">
            <input class="cf-input" :value="blockForm.startDate" placeholder="选择日期" disabled />
          </picker>
          <picker mode="time" :value="blockForm.startTime" @change="blockForm.startTime = $event.detail.value">
            <input class="cf-input" :value="blockForm.startTime" placeholder="选择时间" disabled style="margin-top: 8rpx;" />
          </picker>
        </CfFormItem>
        <CfFormItem label="结束时间" required>
          <picker mode="date" :value="blockForm.endDate" @change="blockForm.endDate = $event.detail.value">
            <input class="cf-input" :value="blockForm.endDate" placeholder="选择日期" disabled />
          </picker>
          <picker mode="time" :value="blockForm.endTime" @change="blockForm.endTime = $event.detail.value">
            <input class="cf-input" :value="blockForm.endTime" placeholder="选择时间" disabled style="margin-top: 8rpx;" />
          </picker>
        </CfFormItem>
        <CfFormItem label="原因">
          <input v-model="blockForm.reason" class="cf-input" placeholder="维护原因（可选）" />
        </CfFormItem>
      </view>
    </CfModal>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfButton from '@/components/ui/CfButton.vue'
import CfEmpty from '@/components/ui/CfEmpty.vue'
import CfModal from '@/components/ui/CfModal.vue'
import CfFormItem from '@/components/ui/CfFormItem.vue'
import type { Court, PricingRule, CourtBlock, Reservation, CourtMedia } from '@/types'
import { getCourt, listCourtMedia } from '@/api/courts'
import { listPricingRules } from '@/api/pricing'
import { listCourtBlocks, createCourtBlock, deleteCourtBlock } from '@/api/court-blocks'
import { listReservations } from '@/api/reservations'

const venueId = ref('')
const courtId = ref('')
const court = ref<Court | null>(null)
const rules = ref<PricingRule[]>([])
const blocks = ref<CourtBlock[]>([])
const recentBookings = ref<Reservation[]>([])
const photos = ref<CourtMedia[]>([])

const showBlockModal = ref(false)
const blockForm = reactive({
  startDate: '',
  startTime: '',
  endDate: '',
  endTime: '',
  reason: '',
})

const surfaceLabels: Record<string, string> = {
  hard: '硬地', clay: '红土', grass: '草地', synthetic: '人工',
}
function surfaceLabel(s: string) { return surfaceLabels[s] ?? s }

const weekdayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
function formatWeekdays(wd: string): string {
  return wd.split(',').map(d => weekdayNames[parseInt(d)] ?? d).join(' ')
}

function formatBlockRange(start: string, end: string): string {
  const s = new Date(start)
  const e = new Date(end)
  const pad = (n: number) => String(n).padStart(2, '0')
  const fmtDate = (d: Date) => `${d.getMonth() + 1}/${d.getDate()}`
  const fmtTime = (d: Date) => `${pad(d.getHours())}:${pad(d.getMinutes())}`
  if (s.toDateString() === e.toDateString()) {
    return `${fmtDate(s)} ${fmtTime(s)} - ${fmtTime(e)}`
  }
  return `${fmtDate(s)} ${fmtTime(s)} - ${fmtDate(e)} ${fmtTime(e)}`
}

function formatSlot(start: string, end: string): string {
  const s = new Date(start)
  const e = new Date(end)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${s.getMonth() + 1}/${s.getDate()} ${pad(s.getHours())}:${pad(s.getMinutes())} - ${pad(e.getHours())}:${pad(e.getMinutes())}`
}

const bookingStatusLabels: Record<string, string> = {
  held: '锁定中', pending_payment: '待支付', confirmed: '已确认',
  checked_in: '已签到', completed: '已完成', cancelled: '已取消',
  admin_cancelled: '管理取消', no_show: '未到场',
}
function bookingStatusLabel(s: string) { return bookingStatusLabels[s] ?? s }
function bookingBadge(s: string): string {
  if (['confirmed', 'checked_in'].includes(s)) return 'cf-badge--green'
  if (['held', 'pending_payment'].includes(s)) return 'cf-badge--amber'
  if (['completed'].includes(s)) return 'cf-badge--blue'
  return 'cf-badge--grey'
}

async function loadData() {
  if (!venueId.value || !courtId.value) return
  try {
    const [c, r, b, bk, media] = await Promise.all([
      getCourt(venueId.value, courtId.value),
      listPricingRules({ court_id: courtId.value }),
      listCourtBlocks(venueId.value, courtId.value),
      listReservations({ court_id: courtId.value, page_size: 5 }),
      listCourtMedia(venueId.value, courtId.value),
    ])
    court.value = c
    rules.value = r
    blocks.value = b
    recentBookings.value = bk.items
    photos.value = media
  } catch (e) {
    console.error('Failed to load court detail', e)
  }
}

onLoad((query) => {
  venueId.value = query?.venueId || ''
  courtId.value = query?.courtId || ''
  loadData()
})

onShow(() => {
  loadData()
})

function goSettings() {
  uni.navigateTo({ url: `/packages/venue/court-edit/index?venueId=${venueId.value}&id=${courtId.value}` })
}

function goPhotos() {
  uni.navigateTo({ url: `/packages/venue/court-photos/index?venueId=${venueId.value}&courtId=${courtId.value}` })
}

function previewPhoto(url: string) {
  uni.previewImage({
    current: url,
    urls: photos.value.map(m => m.url),
  })
}

function goCreateRule() {
  uni.navigateTo({ url: `/packages/pricing/edit/index?venue_id=${venueId.value}&court_id=${courtId.value}` })
}

function goEditRule(ruleId: string) {
  uni.navigateTo({ url: `/packages/pricing/edit/index?id=${ruleId}` })
}

function goBookingList() {
  uni.navigateTo({ url: `/packages/booking/list/index?venue_id=${venueId.value}&court_id=${courtId.value}` })
}

function goBookingDetail(id: string) {
  uni.navigateTo({ url: `/packages/booking/detail/index?id=${id}` })
}

async function createBlock() {
  if (!blockForm.startDate || !blockForm.startTime || !blockForm.endDate || !blockForm.endTime) {
    uni.showToast({ title: '请填写完整时间', icon: 'none' })
    return
  }
  try {
    await createCourtBlock(venueId.value, courtId.value, {
      start_at: `${blockForm.startDate}T${blockForm.startTime}:00`,
      end_at: `${blockForm.endDate}T${blockForm.endTime}:00`,
      reason: blockForm.reason || undefined,
    })
    showBlockModal.value = false
    blockForm.startDate = ''
    blockForm.startTime = ''
    blockForm.endDate = ''
    blockForm.endTime = ''
    blockForm.reason = ''
    // Reload blocks
    blocks.value = await listCourtBlocks(venueId.value, courtId.value)
    uni.showToast({ title: '创建成功', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e?.detail || '创建失败', icon: 'none' })
  }
}

async function deleteBlock(blockId: string) {
  uni.showModal({
    title: '删除维护窗口',
    content: '确定删除此维护窗口？',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await deleteCourtBlock(venueId.value, courtId.value, blockId)
        blocks.value = blocks.value.filter(b => b.id !== blockId)
        uni.showToast({ title: '已删除', icon: 'success' })
      } catch (e: any) {
        uni.showToast({ title: e?.detail || '删除失败', icon: 'none' })
      }
    },
  })
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

.info-card {
  padding: $sp-md;
  margin-bottom: $sp-lg;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12rpx 0;

  & + & {
    border-top: 0.5px solid $cf-glass-border;
  }
}

.info-label {
  font-size: 26rpx;
  color: $cf-text-2;
}

.info-value {
  font-size: 26rpx;
  color: $cf-white;
  font-weight: 600;
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
}

.photo-strip {
  white-space: nowrap;

  &__inner {
    display: inline-flex;
    gap: $sp-sm;
  }

  &__img {
    width: 180rpx;
    height: 180rpx;
    border-radius: $r-md;
    flex-shrink: 0;
  }
}

.rule-card {
  padding: $sp-md;
  margin-bottom: $sp-sm;

  &__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12rpx;
  }

  &__name {
    font-size: 28rpx;
    font-weight: 700;
    color: $cf-white;
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

.block-card {
  padding: $sp-md;
  margin-bottom: $sp-sm;

  &__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  &__time {
    font-size: 26rpx;
    font-weight: 600;
    color: $cf-white;
  }

  &__del {
    padding: 8rpx;
  }

  &__reason {
    font-size: 24rpx;
    color: $cf-text-2;
    margin-top: 8rpx;
  }
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

  &__time {
    font-size: 26rpx;
    font-weight: 600;
    color: $cf-white;
  }

  &__bottom {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  &__user {
    font-size: 24rpx;
    color: $cf-text-2;
  }

  &__price {
    font-size: 26rpx;
    font-weight: 700;
    color: $cf-lime;
  }
}

.block-form {
  padding: $sp-sm 0;
}

.cf-input {
  width: 100%;
  padding: 16rpx 20rpx;
  font-size: 28rpx;
  color: $cf-white;
  background: $cf-glass-bg;
  border: 0.5px solid $cf-glass-border;
  border-radius: $r-sm;
}
</style>
