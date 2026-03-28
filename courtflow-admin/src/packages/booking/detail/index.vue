<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">预约详情</text>
      <view class="page-header__action" />
    </view>

    <scroll-view v-if="reservation" scroll-y class="content">
      <!-- Info card -->
      <view class="info-card cf-glass-card">
        <view class="info-row">
          <text class="info-label">状态</text>
          <view :class="['cf-badge', badgeClass(reservation.status)]">
            {{ statusLabel(reservation.status) }}
          </view>
        </view>
        <view class="info-row">
          <text class="info-label">场地</text>
          <text class="info-value">{{ reservation.court_name }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">场馆</text>
          <text class="info-value">{{ reservation.venue_name }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">时间</text>
          <text class="info-value">{{ formatSlot(reservation.slot_start_at, reservation.slot_end_at) }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">用户</text>
          <text class="info-value">{{ reservation.user_nickname || '未知' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">手机</text>
          <text class="info-value">{{ reservation.contact_phone || reservation.user_phone || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">金额</text>
          <text class="info-value price">&yen;{{ (reservation.amount_cents / 100).toFixed(2) }}</text>
        </view>
        <view v-if="reservation.note" class="info-row">
          <text class="info-label">备注</text>
          <text class="info-value">{{ reservation.note }}</text>
        </view>
        <view v-if="reservation.checked_in_at" class="info-row">
          <text class="info-label">签到时间</text>
          <text class="info-value">{{ formatTime(reservation.checked_in_at) }}</text>
        </view>
        <view v-if="reservation.cancelled_at" class="info-row">
          <text class="info-label">取消时间</text>
          <text class="info-value">{{ formatTime(reservation.cancelled_at) }}</text>
        </view>
        <view v-if="reservation.cancel_reason" class="info-row">
          <text class="info-label">取消原因</text>
          <text class="info-value">{{ reservation.cancel_reason }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">创建时间</text>
          <text class="info-value">{{ formatTime(reservation.created_at) }}</text>
        </view>
      </view>

      <!-- Actions -->
      <view v-if="showActions" class="actions">
        <CfButton
          v-if="canCheckIn"
          type="primary"
          block
          icon="check"
          @click="doCheckIn"
        >签到</CfButton>
        <CfButton
          v-if="canComplete"
          type="primary"
          block
          icon="check"
          @click="doComplete"
        >完成</CfButton>
        <CfButton
          v-if="canNoShow"
          type="secondary"
          block
          @click="doNoShow"
        >标记未到场</CfButton>
        <CfButton
          v-if="canCancel"
          type="danger"
          block
          @click="showCancelModal = true"
        >取消预约</CfButton>
      </view>
    </scroll-view>

    <!-- Cancel modal -->
    <CfModal
      :visible="showCancelModal"
      title="取消预约"
      confirm-text="确认取消"
      confirm-type="danger"
      @close="showCancelModal = false"
      @confirm="doCancel"
    >
      <view class="cancel-form">
        <CfFormItem label="取消原因">
          <input
            v-model="cancelReason"
            class="cf-input"
            placeholder="请输入取消原因（可选）"
          />
        </CfFormItem>
      </view>
    </CfModal>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfButton from '@/components/ui/CfButton.vue'
import CfModal from '@/components/ui/CfModal.vue'
import CfFormItem from '@/components/ui/CfFormItem.vue'
import type { Reservation } from '@/types'
import {
  getReservation,
  cancelReservation,
  checkInReservation,
  noShowReservation,
  completeReservation,
} from '@/api/reservations'

const reservationId = ref('')
const reservation = ref<Reservation | null>(null)
const showCancelModal = ref(false)
const cancelReason = ref('')

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
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${s.getMonth() + 1}月${s.getDate()}日 ${pad(s.getHours())}:${pad(s.getMinutes())} - ${pad(e.getHours())}:${pad(e.getMinutes())}`
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}/${d.getDate()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const canCheckIn = computed(() => reservation.value?.status === 'confirmed')
const canComplete = computed(() => reservation.value?.status === 'checked_in')
const canNoShow = computed(() => ['confirmed', 'checked_in'].includes(reservation.value?.status ?? ''))
const canCancel = computed(() =>
  ['held', 'pending_payment', 'confirmed', 'checked_in'].includes(reservation.value?.status ?? ''),
)
const showActions = computed(() => canCheckIn.value || canComplete.value || canNoShow.value || canCancel.value)

onMounted(() => {
  const pages = getCurrentPages()
  const p = pages[pages.length - 1] as any
  const opts = p?.$page?.options || p?.options || {}
  reservationId.value = opts.id || ''
})

onShow(async () => {
  if (!reservationId.value) return
  try {
    reservation.value = await getReservation(reservationId.value)
  } catch (e) {
    console.error('Failed to load reservation', e)
  }
})

async function doCheckIn() {
  try {
    reservation.value = await checkInReservation(reservationId.value)
    uni.showToast({ title: '签到成功', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e?.detail || '操作失败', icon: 'none' })
  }
}

async function doComplete() {
  try {
    reservation.value = await completeReservation(reservationId.value)
    uni.showToast({ title: '已完成', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e?.detail || '操作失败', icon: 'none' })
  }
}

async function doNoShow() {
  uni.showModal({
    title: '确认标记未到场？',
    content: '此操作将标记该用户未到场',
    success: async (res) => {
      if (!res.confirm) return
      try {
        reservation.value = await noShowReservation(reservationId.value)
        uni.showToast({ title: '已标记未到场', icon: 'success' })
      } catch (e: any) {
        uni.showToast({ title: e?.detail || '操作失败', icon: 'none' })
      }
    },
  })
}

async function doCancel() {
  try {
    reservation.value = await cancelReservation(reservationId.value, cancelReason.value || undefined)
    showCancelModal.value = false
    cancelReason.value = ''
    uni.showToast({ title: '已取消', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e?.detail || '操作失败', icon: 'none' })
  }
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
  flex-shrink: 0;
}

.info-value {
  font-size: 26rpx;
  color: $cf-white;
  font-weight: 600;
  text-align: right;

  &.price {
    color: $cf-lime;
    font-size: 30rpx;
  }
}

.actions {
  display: flex;
  flex-direction: column;
  gap: $sp-sm;
  margin-bottom: $sp-xl;
}

.cancel-form {
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
