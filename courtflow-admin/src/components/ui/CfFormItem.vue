<template>
  <view class="cf-form-item">
    <view class="cf-form-item__header">
      <text class="cf-form-item__label">{{ label }}</text>
      <text v-if="required" class="cf-form-item__required">*</text>
    </view>
    <view class="cf-form-item__body">
      <slot />
    </view>
    <text v-if="hint" class="cf-form-item__hint">{{ hint }}</text>
    <text v-if="error" class="cf-form-item__error">{{ error }}</text>
  </view>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  required?: boolean
  hint?: string
  error?: string
}>()
</script>

<style lang="scss" scoped>
.cf-form-item {
  margin-bottom: $sp-md;

  &__header {
    display: flex;
    align-items: center;
    gap: 4rpx;
    margin-bottom: 12rpx;
  }

  &__label {
    font-size: 26rpx;
    font-weight: 600;
    color: $cf-text-2;
  }

  &__required {
    color: $cf-danger;
    font-size: 26rpx;
  }

  &__body {
    :deep(input),
    :deep(textarea) {
      width: 100%;
      background: $cf-glass-bg;
      border: 0.5px solid $cf-glass-border;
      border-radius: $r-md;
      padding: 20rpx 24rpx;
      color: $cf-white;
      font-size: 28rpx;

      &:focus {
        border-color: $cf-lime;
      }
    }

    :deep(textarea) {
      min-height: 160rpx;
    }
  }

  &__hint {
    font-size: 22rpx;
    color: $cf-text-3;
    margin-top: 8rpx;
  }

  &__error {
    font-size: 22rpx;
    color: $cf-danger;
    margin-top: 8rpx;
  }
}
</style>
