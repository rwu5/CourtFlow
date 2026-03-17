<template>
  <view class="booking-grid">
    <view class="grid-body">
      <!-- Sticky time col -->
      <view class="time-col">
        <view class="time-col__header">
          <text class="time-col__header-text">时间</text>
        </view>
        <view v-for="slot in timeLabels" :key="slot" class="time-cell">
          <text class="time-cell__label">{{ slot }}</text>
        </view>
      </view>

      <!-- Scrollable court columns -->
      <scroll-view class="courts-scroll" scroll-x>
        <view class="courts-inner">
          <view class="court-headers">
            <view v-for="court in courts" :key="court.id" class="court-header">
              <text class="court-header__name">{{ court.name }}</text>
              <text v-if="court.typeName" class="court-header__type">{{ court.typeName }}</text>
            </view>
          </view>

          <view v-for="slot in timeLabels" :key="slot" class="slot-row">
            <view
              v-for="court in courts"
              :key="court.id"
              class="slot-cell"
              :class="getCellClass(court.id, slot)"
              @tap="onCellTap(court.id, slot)"
            >
              <template v-if="getSlot(court.id, slot) as s">
                <template v-if="s.status === 'available' || isSelected(court.id, slot)">
                  <text class="slot-price">¥{{ centsToYuan(s.amount_cents!) }}</text>
                  <text v-if="s.original_amount_cents && s.original_amount_cents !== s.amount_cents" class="slot-orig">¥{{ centsToYuan(s.original_amount_cents) }}</text>
                </template>
                <template v-else-if="s.status === 'held_by_me'">
                  <cf-icon name="clock" :size="14" color="#FBBF24" />
                  <text class="slot-label slot-label--held">锁定中</text>
                </template>
                <template v-else-if="s.status === 'my_booking'">
                  <cf-icon name="check" :size="14" color="#34d399" />
                  <text class="slot-label slot-label--mine">我的预约</text>
                </template>
                <template v-else-if="s.status === 'locked'">
                  <text class="slot-label">关联锁场</text>
                </template>
                <template v-else>
                  <view class="slot-dash" />
                </template>
              </template>
              <template v-else>
                <view class="slot-dash" />
              </template>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- Loading overlay -->
    <view v-if="loading" class="grid-loading">
      <view class="grid-loading__spinner" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'
import type { AvailabilityGrid, SlotInfo } from '../../../types'

interface CourtMeta { id: string; name: string; typeName?: string }
interface DateTab { dateStr: string; mmdd: string; weekday: string; isToday: boolean }

const props = defineProps<{
  grid: AvailabilityGrid
  courts: CourtMeta[]
  selectedDate: string
  dateTabs: DateTab[]
  slotDurationMinutes: number
  openTime: string
  closeTime: string
  selectedSlotKeys: Set<string>
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'select-date', date: string): void
  (e: 'toggle-slot', slot: SlotInfo): void
}>()

const timeLabels = computed(() => {
  const labels: string[] = []
  const [oh, om] = props.openTime.split(':').map(Number)
  const [ch, cm] = props.closeTime.split(':').map(Number)
  let h = oh, m = om
  while (h * 60 + m < ch * 60 + cm) {
    labels.push(`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`)
    m += props.slotDurationMinutes
    if (m >= 60) { h += Math.floor(m / 60); m = m % 60 }
  }
  return labels
})

function getSlot(courtId: string, timeLabel: string): SlotInfo | null {
  const courtSlots = props.grid[courtId]
  if (!courtSlots) return null
  const entry = Object.values(courtSlots).find(s => {
    const d = new Date(s.slot_start)
    return `${String(d.getUTCHours()).padStart(2,'0')}:${String(d.getUTCMinutes()).padStart(2,'0')}` === timeLabel
  })
  if (!entry) return null
  if (props.selectedSlotKeys.has(`${courtId}::${entry.slot_start}`)) return { ...entry, status: 'selected' }
  return entry
}

function isSelected(courtId: string, timeLabel: string): boolean {
  const s = getSlot(courtId, timeLabel)
  return s ? props.selectedSlotKeys.has(`${courtId}::${s.slot_start}`) : false
}

function getCellClass(courtId: string, timeLabel: string): string {
  const s = getSlot(courtId, timeLabel)
  if (!s) return 'slot-cell--unavailable'
  return `slot-cell--${isSelected(courtId, timeLabel) ? 'selected' : s.status}`
}

function onCellTap(courtId: string, timeLabel: string) {
  const s = getSlot(courtId, timeLabel)
  if (!s || (s.status !== 'available' && !isSelected(courtId, timeLabel))) return
  emit('toggle-slot', s)
}

function centsToYuan(cents: number): string { return (cents / 100).toFixed(0) }
</script>

<style lang="scss">
@import '@/uni.scss';

.booking-grid { position: relative; background: $cf-bg; }

.grid-body { display: flex; flex-direction: row; overflow: hidden; }

// Time column
.time-col {
  width: 110rpx; flex-shrink: 0;
  border-right: 0.5px solid $cf-line;
  background: rgba(8,14,11,0.9);
  z-index: 10; backdrop-filter: blur(8px);
}
.time-col__header {
  height: 80rpx; border-bottom: 0.5px solid $cf-line;
  display: flex; align-items: center; justify-content: center;
}
.time-col__header-text { font-size: 17rpx; color: $cf-text-3; letter-spacing: 0.06em; font-weight: 600; }
.time-cell {
  height: 110rpx; display: flex; align-items: center; justify-content: center;
  border-bottom: 0.5px solid $cf-line;
}
.time-cell__label { font-size: 20rpx; color: $cf-text-2; font-weight: 500; }

// Courts
.courts-scroll { flex: 1; }
.courts-inner { display: flex; flex-direction: column; }
.court-headers {
  display: flex; flex-direction: row; height: 80rpx;
  border-bottom: 0.5px solid $cf-line;
  background: rgba(8,14,11,0.9); backdrop-filter: blur(8px);
  position: sticky; top: 0; z-index: 5;
}
.court-header {
  width: 180rpx; flex-shrink: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  border-right: 0.5px solid $cf-line; gap: 4rpx;
}
.court-header__name { font-size: 24rpx; font-weight: 700; color: $cf-white; }
.court-header__type {
  font-size: 17rpx; color: $cf-text-2;
  background: rgba(45,139,87,0.12); border: 0.5px solid rgba(45,139,87,0.25);
  border-radius: $r-full; padding: 2rpx 10rpx;
}

// Slot rows
.slot-row { display: flex; flex-direction: row; height: 110rpx; }
.slot-cell {
  width: 180rpx; flex-shrink: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  border-right: 0.5px solid $cf-line;
  border-bottom: 0.5px solid $cf-line;
  padding: 8rpx; cursor: pointer; position: relative;

  &--available {
    background: rgba(255,255,255,0.025);
    &:active { background: rgba(45,139,87,0.08); }
  }
  &--selected {
    background: rgba(45,139,87,0.18);
    border-color: rgba(45,139,87,0.5) !important;
    box-shadow: inset 0 0 0 1.5rpx rgba(45,139,87,0.6),
                0 0 20rpx rgba(45,139,87,0.15);
  }
  &--unavailable, &--booked, &--locked {
    background: transparent; cursor: default;
  }
  &--held_by_me {
    background: rgba(251,191,36,0.12);
    border-color: rgba(251,191,36,0.4) !important;
    box-shadow: inset 0 0 0 1.5rpx rgba(251,191,36,0.5);
  }
  &--my_booking {
    background: rgba(46,134,193,0.14);
    border-color: rgba(46,134,193,0.4) !important;
    box-shadow: inset 0 0 0 1.5rpx rgba(46,134,193,0.5);
  }
}

.slot-price {
  font-size: 27rpx; font-weight: 800; color: $cf-white;
  .slot-cell--selected & { color: #4ade80; }
}
.slot-orig { font-size: 17rpx; color: $cf-text-3; text-decoration: line-through; margin-top: 2rpx; }
.slot-icon { font-size: 24rpx; margin-bottom: 4rpx; }
.slot-label {
  font-size: 17rpx; color: $cf-text-3;
  &--held { color: $cf-amber; font-weight: 600; }
  &--mine { color: $cf-blue; font-weight: 600; }
}
.slot-dash { width: 32rpx; height: 1.5rpx; background: $cf-text-3; opacity: 0.25; border-radius: $r-full; }

// Loading
.grid-loading {
  position: absolute; inset: 0;
  background: rgba(8,14,11,0.72);
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(6px);
}
.grid-loading__spinner {
  width: 60rpx; height: 60rpx;
  border: 3.5rpx solid rgba(255,255,255,0.1);
  border-top-color: $cf-lime;
  border-radius: $r-full;
  animation: spin 0.7s linear infinite;
}
</style>
