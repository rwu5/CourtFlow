<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">{{ isEdit ? '编辑定价规则' : '新建定价规则' }}</text>
      <view style="width: 44rpx" />
    </view>

    <scroll-view scroll-y class="content">
      <!-- Venue picker -->
      <CfFormItem label="所属场馆" required>
        <picker :value="venueIndex" :range="venueOptions" range-key="label" @change="onVenueChange">
          <view class="cf-select">
            <text :class="['cf-select__text', !form.venue_id && 'cf-select__placeholder']">
              {{ selectedVenueLabel || '请选择场馆' }}
            </text>
            <CfIcon name="chevron-down" :size="16" color="rgba(255,255,255,0.4)" />
          </view>
        </picker>
      </CfFormItem>

      <!-- Court picker (optional, depends on venue) -->
      <CfFormItem label="指定场地" hint="不选则适用于该场馆所有场地">
        <picker :value="courtIndex" :range="courtOptions" range-key="label" :disabled="!form.venue_id" @change="onCourtChange">
          <view class="cf-select" :class="{ 'cf-select--disabled': !form.venue_id }">
            <text :class="['cf-select__text', !form.court_id && 'cf-select__placeholder']">
              {{ selectedCourtLabel || '全部场地' }}
            </text>
            <CfIcon name="chevron-down" :size="16" color="rgba(255,255,255,0.4)" />
          </view>
        </picker>
      </CfFormItem>

      <CfFormItem label="规则名称" required>
        <input v-model="form.name" placeholder="如：工作日白天标准价" />
      </CfFormItem>

      <CfFormItem label="价格 (元)" required>
        <input v-model="form.amount_yuan" type="digit" placeholder="如：120" />
      </CfFormItem>

      <CfFormItem label="原价 (元)" hint="划线价，可选">
        <input v-model="form.original_yuan" type="digit" placeholder="如：150" />
      </CfFormItem>

      <CfFormItem label="优先级" hint="数字越大优先级越高">
        <input v-model="form.priority" type="number" placeholder="0" />
      </CfFormItem>

      <CfFormItem label="适用工作日" hint="选择适用的日期">
        <view class="weekday-row">
          <view
            v-for="(label, i) in weekdayLabels"
            :key="i"
            :class="['option-chip', { 'option-chip--active': selectedWeekdays.includes(i) }]"
            @click="toggleWeekday(i)"
          >{{ label }}</view>
        </view>
      </CfFormItem>

      <view class="time-row">
        <CfFormItem label="开始时间">
          <input v-model="form.time_from" placeholder="08:00" />
        </CfFormItem>
        <CfFormItem label="结束时间">
          <input v-model="form.time_to" placeholder="18:00" />
        </CfFormItem>
      </view>

      <view style="padding: 24rpx 0 48rpx">
        <CfButton type="primary" size="lg" block :disabled="saving" @click="handleSave">
          {{ saving ? '保存中...' : '保存' }}
        </CfButton>
        <view v-if="isEdit" style="margin-top: 16rpx">
          <CfButton type="danger" size="md" block @click="handleDelete">删除规则</CfButton>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfFormItem from '@/components/ui/CfFormItem.vue'
import CfButton from '@/components/ui/CfButton.vue'
import type { Venue, Court } from '@/types'
import { getPricingRule, createPricingRule, updatePricingRule, deletePricingRule } from '@/api/pricing'
import { listVenues } from '@/api/venues'
import { listCourts } from '@/api/courts'

const ruleId = ref('')
const isEdit = ref(false)
const saving = ref(false)

// Venue & court selection
const venues = ref<Venue[]>([])
const courts = ref<Court[]>([])

const venueOptions = computed(() => venues.value.map(v => ({ id: v.id, label: v.short_name || v.name })))
const courtOptions = computed(() => [
  { id: '', label: '全部场地' },
  ...courts.value.map(c => ({ id: c.id, label: c.name })),
])

const venueIndex = computed(() => {
  if (!form.value.venue_id) return -1
  return venues.value.findIndex(v => v.id === form.value.venue_id)
})
const courtIndex = computed(() => {
  if (!form.value.court_id) return 0
  return courts.value.findIndex(c => c.id === form.value.court_id) + 1
})

const selectedVenueLabel = computed(() => {
  const v = venues.value.find(v => v.id === form.value.venue_id)
  return v ? (v.short_name || v.name) : ''
})
const selectedCourtLabel = computed(() => {
  if (!form.value.court_id) return ''
  const c = courts.value.find(c => c.id === form.value.court_id)
  return c?.name || ''
})

const weekdayLabels = ['一', '二', '三', '四', '五', '六', '日']
const selectedWeekdays = ref<number[]>([])

const form = ref({
  venue_id: '',
  court_id: '',
  name: '',
  amount_yuan: '',
  original_yuan: '',
  priority: '0',
  time_from: '',
  time_to: '',
})

function toggleWeekday(i: number) {
  const idx = selectedWeekdays.value.indexOf(i)
  if (idx >= 0) selectedWeekdays.value.splice(idx, 1)
  else selectedWeekdays.value.push(i)
}

async function onVenueChange(e: any) {
  const idx = parseInt(e.detail.value)
  if (idx < 0 || idx >= venues.value.length) return
  form.value.venue_id = venues.value[idx].id
  form.value.court_id = ''
  try {
    courts.value = await listCourts(form.value.venue_id)
  } catch {
    courts.value = []
  }
}

function onCourtChange(e: any) {
  const idx = parseInt(e.detail.value)
  // index 0 = "全部场地" (no court)
  form.value.court_id = idx > 0 ? courts.value[idx - 1].id : ''
}

onMounted(async () => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1] as any
  const opts = page?.$page?.options || page?.options || {}

  // Load venues
  try {
    venues.value = await listVenues()
  } catch {}

  if (opts.id) {
    ruleId.value = opts.id
    isEdit.value = true
    await loadRule(opts.id)
  } else {
    // Prefill from query params
    if (opts.venue_id) {
      form.value.venue_id = opts.venue_id
      try {
        courts.value = await listCourts(opts.venue_id)
      } catch {}
    }
    if (opts.court_id) form.value.court_id = opts.court_id
  }
})

async function loadRule(id: string) {
  try {
    const r = await getPricingRule(id)
    form.value = {
      venue_id: r.venue_id,
      court_id: r.court_id || '',
      name: r.name,
      amount_yuan: String(r.amount_cents / 100),
      original_yuan: r.original_amount_cents ? String(r.original_amount_cents / 100) : '',
      priority: String(r.priority),
      time_from: r.time_from ?? '',
      time_to: r.time_to ?? '',
    }
    if (r.weekdays) {
      selectedWeekdays.value = r.weekdays.split(',').map(Number)
    }
    // Load courts for the rule's venue
    if (r.venue_id) {
      try {
        courts.value = await listCourts(r.venue_id)
      } catch {}
    }
  } catch {}
}

async function handleSave() {
  if (!form.value.name || !form.value.amount_yuan || !form.value.venue_id) {
    uni.showToast({ title: '请填写必填项', icon: 'none' })
    return
  }
  saving.value = true
  try {
    const data: any = {
      name: form.value.name,
      amount_cents: Math.round(parseFloat(form.value.amount_yuan) * 100),
      original_amount_cents: form.value.original_yuan
        ? Math.round(parseFloat(form.value.original_yuan) * 100)
        : null,
      priority: parseInt(form.value.priority) || 0,
      weekdays: selectedWeekdays.value.length
        ? selectedWeekdays.value.sort().join(',')
        : null,
      time_from: form.value.time_from || null,
      time_to: form.value.time_to || null,
      court_id: form.value.court_id || null,
    }
    if (isEdit.value) {
      await updatePricingRule(ruleId.value, data)
    } else {
      data.venue_id = form.value.venue_id
      await createPricingRule(data)
    }
    uni.showToast({ title: '保存成功' })
    uni.navigateBack()
  } catch (e: any) {
    uni.showToast({ title: e.detail ?? '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除该定价规则吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await deletePricingRule(ruleId.value)
          uni.showToast({ title: '已删除' })
          uni.navigateBack()
        } catch (e: any) {
          uni.showToast({ title: e.detail ?? '删除失败', icon: 'none' })
        }
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
  &__title { font-size: 32rpx; font-weight: 700; color: $cf-white; }
}

.content {
  padding: $sp-md;
  height: calc(100vh - 160rpx - env(safe-area-inset-top));
}

.cf-select {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 16rpx 20rpx;
  font-size: 28rpx;
  background: $cf-glass-bg;
  border: 0.5px solid $cf-glass-border;
  border-radius: $r-sm;

  &--disabled {
    opacity: 0.5;
  }

  &__text {
    color: $cf-white;
  }

  &__placeholder {
    color: $cf-text-3;
  }
}

.time-row {
  display: flex;
  gap: $sp-sm;
  > * { flex: 1; }
}

.weekday-row {
  display: flex;
  gap: 12rpx;
}

.option-chip {
  padding: 12rpx 24rpx;
  border-radius: $r-full;
  font-size: 26rpx;
  color: $cf-text-2;
  background: $cf-glass-bg;
  border: 0.5px solid $cf-glass-border;

  &--active {
    color: $cf-lime;
    border-color: rgba(184, 212, 48, 0.4);
    background: rgba(184, 212, 48, 0.12);
  }
}
</style>
