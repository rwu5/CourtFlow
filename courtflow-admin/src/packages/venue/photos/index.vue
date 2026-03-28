<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">场馆照片</text>
      <view style="width: 44rpx" />
    </view>

    <scroll-view scroll-y class="content">
      <CfFormItem label="场馆照片" hint="最多上传 9 张">
        <CfImageUpload v-model="photos" :max="9" />
      </CfFormItem>

      <view style="padding-top: 24rpx">
        <CfButton type="primary" size="lg" block :disabled="saving" @click="handleSave">
          {{ saving ? '保存中...' : '保存' }}
        </CfButton>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfFormItem from '@/components/ui/CfFormItem.vue'
import CfImageUpload from '@/components/ui/CfImageUpload.vue'
import CfButton from '@/components/ui/CfButton.vue'
import { getVenue } from '@/api/venues'

const venueId = ref('')
const photos = ref<string[]>([])
const saving = ref(false)

onMounted(async () => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1] as any
  venueId.value = page?.$page?.options?.venueId || page?.options?.venueId || ''
  if (venueId.value) {
    try {
      const v = await getVenue(venueId.value)
      photos.value = v.photos ?? []
    } catch {}
  }
})

async function handleSave() {
  saving.value = true
  try {
    // TODO: sync photos via media API (add/delete diff)
    uni.showToast({ title: '保存成功' })
    uni.navigateBack()
  } catch (e: any) {
    uni.showToast({ title: e.detail ?? '保存失败', icon: 'none' })
  } finally {
    saving.value = false
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
  &__title { font-size: 32rpx; font-weight: 700; color: $cf-white; }
}

.content {
  padding: $sp-md;
  height: calc(100vh - 160rpx - env(safe-area-inset-top));
}
</style>
