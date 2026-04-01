<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">设施管理</text>
      <CfButton type="primary" size="sm" icon="plus" @click="showAdd = true">添加</CfButton>
    </view>

    <scroll-view scroll-y class="content">
      <CfEmpty v-if="!facilities.length" icon="wrench" text="暂无设施信息" />
      <view
        v-for="f in facilities"
        :key="f.id"
        class="facility-item cf-glass-card"
      >
        <view class="facility-item__info">
          <text class="facility-item__label">{{ f.label }}</text>
          <text class="facility-item__desc">{{ f.description ?? '' }}</text>
        </view>
        <view class="facility-item__del" @click="handleDelete(f.id)">
          <CfIcon name="trash" :size="18" color="#F04545" />
        </view>
      </view>
    </scroll-view>

    <!-- Add Modal -->
    <CfModal
      :visible="showAdd"
      title="添加设施"
      confirm-text="添加"
      confirm-type="primary"
      :show-footer="true"
      @close="showAdd = false"
      @confirm="handleAdd"
    >
      <CfFormItem label="设施名称" required>
        <input v-model="newFacility.label" placeholder="如：停车场" />
      </CfFormItem>
      <CfFormItem label="标识 Key" required>
        <input v-model="newFacility.key" placeholder="如：parking" />
      </CfFormItem>
      <CfFormItem label="描述">
        <input v-model="newFacility.description" placeholder="可选描述" />
      </CfFormItem>
    </CfModal>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfButton from '@/components/ui/CfButton.vue'
import CfEmpty from '@/components/ui/CfEmpty.vue'
import CfModal from '@/components/ui/CfModal.vue'
import CfFormItem from '@/components/ui/CfFormItem.vue'
import type { VenueFacility } from '@/types'
import { listVenueFacilities, addVenueFacility, deleteVenueFacility } from '@/api/venues'

const venueId = ref('')
const facilities = ref<VenueFacility[]>([])
const showAdd = ref(false)
const newFacility = ref({ key: '', label: '', description: '' })

async function loadData() {
  if (!venueId.value) return
  try { facilities.value = await listVenueFacilities(venueId.value) } catch {}
}

onLoad((query) => {
  venueId.value = query?.venueId || ''
  loadData()
})

onShow(() => {
  loadData()
})

async function handleAdd() {
  if (!newFacility.value.key || !newFacility.value.label) {
    uni.showToast({ title: '请填写必填项', icon: 'none' })
    return
  }
  try {
    await addVenueFacility(venueId.value, {
      key: newFacility.value.key,
      label: newFacility.value.label,
      description: newFacility.value.description || null,
    } as any)
    showAdd.value = false
    newFacility.value = { key: '', label: '', description: '' }
    facilities.value = await listVenueFacilities(venueId.value)
  } catch (e: any) {
    uni.showToast({ title: e.detail ?? '添加失败', icon: 'none' })
  }
}

async function handleDelete(id: string) {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除该设施？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteVenueFacility(venueId.value, id)
          facilities.value = facilities.value.filter(f => f.id !== id)
        } catch {}
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
}

.content {
  padding: $sp-md;
  height: calc(100vh - 160rpx - env(safe-area-inset-top));
}

.facility-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $sp-md;
  margin-bottom: $sp-sm;

  &__info { flex: 1; }
  &__label { font-size: 28rpx; font-weight: 600; color: $cf-white; display: block; }
  &__desc { font-size: 24rpx; color: $cf-text-2; }
  &__del { padding: 16rpx; }
}
</style>
