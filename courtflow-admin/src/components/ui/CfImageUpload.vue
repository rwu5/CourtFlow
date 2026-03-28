<template>
  <view class="cf-upload">
    <view v-for="(img, i) in modelValue" :key="i" class="cf-upload__item">
      <image :src="img" class="cf-upload__img" mode="aspectFill" />
      <view class="cf-upload__remove" @click="removeImage(i)">
        <CfIcon name="close" :size="14" color="#fff" />
      </view>
    </view>
    <view v-if="modelValue.length < max" class="cf-upload__add" @click="chooseImage">
      <CfIcon name="plus" :size="28" color="rgba(255,255,255,0.3)" />
      <text class="cf-upload__tip">上传图片</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import CfIcon from './CfIcon.vue'

const props = defineProps<{
  modelValue: string[]
  max?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const max = props.max ?? 9

function removeImage(index: number) {
  const list = [...props.modelValue]
  list.splice(index, 1)
  emit('update:modelValue', list)
}

function chooseImage() {
  const remaining = max - props.modelValue.length
  uni.chooseImage({
    count: remaining,
    success(res) {
      // TODO: upload to S3 and get URLs — for now use local paths
      emit('update:modelValue', [...props.modelValue, ...res.tempFilePaths])
    },
  })
}
</script>

<style lang="scss" scoped>
.cf-upload {
  display: flex;
  flex-wrap: wrap;
  gap: $sp-sm;

  &__item {
    position: relative;
    width: 160rpx;
    height: 160rpx;
    border-radius: $r-md;
    overflow: hidden;
  }

  &__img {
    width: 100%;
    height: 100%;
  }

  &__remove {
    position: absolute;
    top: 4rpx;
    right: 4rpx;
    width: 36rpx;
    height: 36rpx;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__add {
    width: 160rpx;
    height: 160rpx;
    border-radius: $r-md;
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
