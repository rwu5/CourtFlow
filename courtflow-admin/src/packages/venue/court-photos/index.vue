<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">场地照片</text>
      <view style="width: 44rpx" />
    </view>

    <scroll-view scroll-y class="content">
      <view class="photo-grid">
        <view v-for="m in mediaList" :key="m.id" class="photo-item">
          <image :src="m.url" class="photo-item__img" mode="aspectFill" @click="previewImage(m.url)" />
          <view class="photo-item__remove" @click="handleDelete(m.id)">
            <CfIcon name="close" :size="14" color="#fff" />
          </view>
        </view>
        <view v-if="mediaList.length < 9" class="photo-item photo-item--add" @click="chooseImage">
          <CfIcon name="plus" :size="28" color="rgba(255,255,255,0.3)" />
          <text class="photo-item__tip">添加照片</text>
        </view>
      </view>

      <CfEmpty v-if="!mediaList.length && !loading" icon="image" text="暂无场地照片" />
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfEmpty from '@/components/ui/CfEmpty.vue'
import type { CourtMedia } from '@/types'
import { listCourtMedia, addCourtMedia, deleteCourtMedia } from '@/api/courts'

const venueId = ref('')
const courtId = ref('')
const mediaList = ref<CourtMedia[]>([])
const loading = ref(false)

onLoad((query) => {
  venueId.value = query?.venueId || ''
  courtId.value = query?.courtId || ''
  load()
})

onShow(() => {
  load()
})

async function load() {
  loading.value = true
  try {
    mediaList.value = await listCourtMedia(venueId.value, courtId.value)
  } catch (e) {
    console.error('Failed to load court media', e)
  } finally {
    loading.value = false
  }
}

function chooseImage() {
  const remaining = 9 - mediaList.value.length
  uni.chooseImage({
    count: remaining,
    async success(res) {
      for (const path of res.tempFilePaths) {
        try {
          // TODO: upload to S3 and get real URL — for now use local path
          await addCourtMedia(venueId.value, courtId.value, {
            url: path,
            media_type: 'photo',
            sort_order: mediaList.value.length,
          })
        } catch (e: any) {
          uni.showToast({ title: e?.detail || '上传失败', icon: 'none' })
          return
        }
      }
      await load()
      uni.showToast({ title: '添加成功', icon: 'success' })
    },
  })
}

function handleDelete(mediaId: string) {
  uni.showModal({
    title: '删除照片',
    content: '确定删除此照片？',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await deleteCourtMedia(venueId.value, courtId.value, mediaId)
        mediaList.value = mediaList.value.filter(m => m.id !== mediaId)
        uni.showToast({ title: '已删除', icon: 'success' })
      } catch (e: any) {
        uni.showToast({ title: e?.detail || '删除失败', icon: 'none' })
      }
    },
  })
}

function previewImage(url: string) {
  uni.previewImage({
    current: url,
    urls: mediaList.value.map(m => m.url),
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

.photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: $sp-sm;
}

.photo-item {
  position: relative;
  width: 200rpx;
  height: 200rpx;
  border-radius: $r-md;
  overflow: hidden;

  &__img {
    width: 100%;
    height: 100%;
  }

  &__remove {
    position: absolute;
    top: 8rpx;
    right: 8rpx;
    width: 40rpx;
    height: 40rpx;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &--add {
    border: 1px dashed rgba(255, 255, 255, 0.15);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8rpx;
  }

  &__tip {
    font-size: 20rpx;
    color: rgba(255, 255, 255, 0.3);
  }
}
</style>
