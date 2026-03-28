<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">{{ isEdit ? '编辑场地' : '新建场地' }}</text>
      <view style="width: 44rpx" />
    </view>

    <scroll-view scroll-y class="content">
      <CfFormItem label="场地名称" required>
        <input v-model="form.name" placeholder="如：1号场" />
      </CfFormItem>

      <CfFormItem label="地面类型">
        <view class="option-row">
          <view
            v-for="s in surfaces"
            :key="s.value"
            :class="['option-chip', { 'option-chip--active': form.surface === s.value }]"
            @click="form.surface = s.value"
          >
            {{ s.label }}
          </view>
        </view>
      </CfFormItem>

      <CfFormItem label="场地类型">
        <view class="option-row">
          <view
            :class="['option-chip', { 'option-chip--active': form.is_indoor }]"
            @click="form.is_indoor = true"
          >室内</view>
          <view
            :class="['option-chip', { 'option-chip--active': !form.is_indoor }]"
            @click="form.is_indoor = false"
          >室外</view>
        </view>
      </CfFormItem>

      <CfFormItem label="时段长度(分钟)">
        <input v-model="form.slot_duration_minutes" type="number" placeholder="60" />
      </CfFormItem>

      <CfFormItem label="排序序号">
        <input v-model="form.sort_order" type="number" placeholder="0" />
      </CfFormItem>

      <view style="padding: 24rpx 0 48rpx">
        <CfButton type="primary" size="lg" block :disabled="saving" @click="handleSave">
          {{ saving ? '保存中...' : '保存' }}
        </CfButton>
        <view v-if="isEdit" style="margin-top: 16rpx">
          <CfButton type="danger" size="md" block @click="handleDelete">删除场地</CfButton>
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
import { getCourt, createCourt, updateCourt, deleteCourt } from '@/api/courts'

const venueId = ref('')
const courtId = ref('')
const isEdit = ref(false)
const saving = ref(false)

const surfaces = [
  { value: 'hard', label: '硬地' },
  { value: 'clay', label: '红土' },
  { value: 'grass', label: '草地' },
  { value: 'synthetic', label: '人工' },
]

const form = ref({
  name: '',
  surface: 'hard' as string,
  is_indoor: true,
  slot_duration_minutes: 60,
  sort_order: 0,
})

onMounted(() => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1] as any
  const opts = page?.$page?.options || page?.options || {}
  venueId.value = opts.venueId || ''
  if (opts.id) {
    courtId.value = opts.id
    isEdit.value = true
    loadCourt()
  }
})

async function loadCourt() {
  try {
    const c = await getCourt(venueId.value, courtId.value)
    form.value = {
      name: c.name,
      surface: c.surface ?? 'hard',
      is_indoor: c.is_indoor,
      slot_duration_minutes: c.slot_duration_minutes ?? 60,
      sort_order: c.sort_order,
    }
  } catch {}
}

async function handleSave() {
  if (!form.value.name) {
    uni.showToast({ title: '请输入场地名称', icon: 'none' })
    return
  }
  saving.value = true
  try {
    const data: any = {
      ...form.value,
      slot_duration_minutes: Number(form.value.slot_duration_minutes),
      sort_order: Number(form.value.sort_order),
    }
    if (isEdit.value) {
      await updateCourt(venueId.value, courtId.value, data)
    } else {
      await createCourt(venueId.value, data)
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
    content: '确定要删除该场地吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteCourt(venueId.value, courtId.value)
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
