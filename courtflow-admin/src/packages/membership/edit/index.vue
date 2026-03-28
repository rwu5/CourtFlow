<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">{{ isEdit ? '编辑会员方案' : '新建会员方案' }}</text>
      <view style="width: 44rpx" />
    </view>

    <scroll-view scroll-y class="content">
      <CfFormItem label="方案名称" required>
        <input v-model="form.name" placeholder="如：月卡会员" />
      </CfFormItem>

      <CfFormItem label="描述">
        <textarea v-model="form.description" placeholder="方案描述" />
      </CfFormItem>

      <CfFormItem label="适用范围" required>
        <view class="option-row">
          <view
            v-for="s in scopes"
            :key="s.value"
            :class="['option-chip', { 'option-chip--active': form.scope === s.value }]"
            @click="form.scope = s.value"
          >{{ s.label }}</view>
        </view>
      </CfFormItem>

      <CfFormItem label="价格 (元)" required>
        <input v-model="form.price_yuan" type="digit" placeholder="如：299" />
      </CfFormItem>

      <CfFormItem label="有效天数" required>
        <input v-model="form.duration_days" type="number" placeholder="30" />
      </CfFormItem>

      <CfFormItem label="订场折扣 (%)" hint="0 = 不打折">
        <input v-model="form.price_discount_pct" type="number" placeholder="0" />
      </CfFormItem>

      <CfFormItem label="提前预订天数">
        <input v-model="form.booking_window_days" type="number" placeholder="7" />
      </CfFormItem>

      <CfFormItem label="月时长配额 (小时)" hint="留空 = 不限">
        <input v-model="form.monthly_hour_quota" type="number" placeholder="" />
      </CfFormItem>

      <CfFormItem label="最大并发预订数" hint="留空 = 不限">
        <input v-model="form.max_concurrent_bookings" type="number" placeholder="" />
      </CfFormItem>

      <view style="padding: 24rpx 0 48rpx">
        <CfButton type="primary" size="lg" block :disabled="saving" @click="handleSave">
          {{ saving ? '保存中...' : '保存' }}
        </CfButton>
        <view v-if="isEdit" style="margin-top: 16rpx">
          <CfButton type="danger" size="md" block @click="handleDelete">删除方案</CfButton>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfFormItem from '@/components/ui/CfFormItem.vue'
import CfButton from '@/components/ui/CfButton.vue'
import {
  getMembershipTier,
  createMembershipTier,
  updateMembershipTier,
  deleteMembershipTier,
} from '@/api/memberships'

const tierId = ref('')
const isEdit = ref(false)
const saving = ref(false)

const scopes = [
  { value: 'organization', label: '全机构' },
  { value: 'venue', label: '场馆级' },
  { value: 'court_type', label: '场地类型' },
  { value: 'court', label: '单场地' },
]

const form = ref({
  name: '',
  description: '',
  scope: 'organization',
  price_yuan: '',
  duration_days: '30',
  price_discount_pct: '0',
  booking_window_days: '7',
  monthly_hour_quota: '',
  max_concurrent_bookings: '',
})

onMounted(() => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1] as any
  const opts = page?.$page?.options || page?.options || {}
  if (opts.id) {
    tierId.value = opts.id
    isEdit.value = true
    loadTier(opts.id)
  }
})

async function loadTier(id: string) {
  try {
    const t = await getMembershipTier(id)
    form.value = {
      name: t.name,
      description: t.description ?? '',
      scope: t.scope,
      price_yuan: String(t.price_cents / 100),
      duration_days: String(t.duration_days),
      price_discount_pct: String(t.price_discount_pct),
      booking_window_days: String(t.booking_window_days),
      monthly_hour_quota: t.monthly_hour_quota != null ? String(t.monthly_hour_quota) : '',
      max_concurrent_bookings: t.max_concurrent_bookings != null ? String(t.max_concurrent_bookings) : '',
    }
  } catch {}
}

async function handleSave() {
  if (!form.value.name || !form.value.price_yuan) {
    uni.showToast({ title: '请填写必填项', icon: 'none' })
    return
  }
  saving.value = true
  try {
    const data: any = {
      name: form.value.name,
      description: form.value.description || null,
      scope: form.value.scope,
      price_cents: Math.round(parseFloat(form.value.price_yuan) * 100),
      duration_days: parseInt(form.value.duration_days) || 30,
      price_discount_pct: parseInt(form.value.price_discount_pct) || 0,
      booking_window_days: parseInt(form.value.booking_window_days) || 7,
      monthly_hour_quota: form.value.monthly_hour_quota
        ? parseInt(form.value.monthly_hour_quota)
        : null,
      max_concurrent_bookings: form.value.max_concurrent_bookings
        ? parseInt(form.value.max_concurrent_bookings)
        : null,
    }
    if (isEdit.value) {
      await updateMembershipTier(tierId.value, data)
    } else {
      await createMembershipTier(data)
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
    content: '确定要删除该会员方案吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteMembershipTier(tierId.value)
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

.option-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.option-chip {
  padding: 12rpx 28rpx;
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
