<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">{{ isEdit ? '编辑场馆' : '新建场馆' }}</text>
      <view style="width: 44rpx" />
    </view>

    <scroll-view scroll-y class="content">
      <CfFormItem label="场馆名称" required>
        <input v-model="form.name" placeholder="输入场馆名称" />
      </CfFormItem>

      <CfFormItem label="简称">
        <input v-model="form.short_name" placeholder="可选" />
      </CfFormItem>

      <CfFormItem label="城市" required>
        <input v-model="form.city" placeholder="如：上海" />
      </CfFormItem>

      <CfFormItem label="区域">
        <input v-model="form.district" placeholder="如：浦东新区" />
      </CfFormItem>

      <CfFormItem label="详细地址" required>
        <input v-model="form.address" placeholder="输入详细地址" />
      </CfFormItem>

      <CfFormItem label="联系电话">
        <input v-model="form.phone" type="tel" placeholder="场馆联系电话" />
      </CfFormItem>

      <CfFormItem label="微信客服">
        <input v-model="form.wechat_cs" placeholder="微信号" />
      </CfFormItem>

      <CfFormItem label="停车信息">
        <textarea v-model="form.parking_info" placeholder="停车场信息" />
      </CfFormItem>

      <view class="time-row">
        <CfFormItem label="开始营业" required>
          <input v-model="form.open_time" placeholder="07:00" />
        </CfFormItem>
        <CfFormItem label="结束营业" required>
          <input v-model="form.close_time" placeholder="22:00" />
        </CfFormItem>
      </view>

      <view style="padding: 24rpx 0 48rpx">
        <CfButton type="primary" size="lg" block :disabled="saving" @click="handleSave">
          {{ saving ? '保存中...' : '保存' }}
        </CfButton>
        <view v-if="isEdit" style="margin-top: 16rpx">
          <CfButton type="danger" size="md" block @click="handleDelete">删除场馆</CfButton>
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
import { getVenue, createVenue, updateVenue, deleteVenue } from '@/api/venues'

const venueId = ref('')
const isEdit = ref(false)
const saving = ref(false)

const form = ref({
  name: '',
  short_name: '',
  city: '',
  district: '',
  address: '',
  phone: '',
  wechat_cs: '',
  parking_info: '',
  open_time: '07:00',
  close_time: '22:00',
})

onMounted(() => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1] as any
  const id = page?.$page?.options?.id || page?.options?.id
  if (id) {
    venueId.value = id
    isEdit.value = true
    loadVenue(id)
  }
})

async function loadVenue(id: string) {
  try {
    const v = await getVenue(id)
    form.value = {
      name: v.name,
      short_name: v.short_name ?? '',
      city: v.city,
      district: v.district ?? '',
      address: v.address,
      phone: v.phone ?? '',
      wechat_cs: v.wechat_cs ?? '',
      parking_info: v.parking_info ?? '',
      open_time: v.open_time,
      close_time: v.close_time,
    }
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

async function handleSave() {
  if (!form.value.name || !form.value.city || !form.value.address) {
    uni.showToast({ title: '请填写必填项', icon: 'none' })
    return
  }
  saving.value = true
  try {
    const data: any = {
      ...form.value,
      short_name: form.value.short_name || null,
      district: form.value.district || null,
      phone: form.value.phone || null,
      wechat_cs: form.value.wechat_cs || null,
      parking_info: form.value.parking_info || null,
    }
    if (isEdit.value) {
      await updateVenue(venueId.value, data)
    } else {
      await createVenue(data)
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
    content: '确定要删除该场馆吗？此操作不可撤回',
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteVenue(venueId.value)
          uni.showToast({ title: '已删除' })
          uni.navigateBack({ delta: 2 })
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

.time-row {
  display: flex;
  gap: $sp-sm;

  > * { flex: 1; }
}
</style>
