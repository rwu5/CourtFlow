<template>
  <view class="cf-empty">
    <CfIcon :name="icon" :size="48" color="rgba(255,255,255,0.15)" />
    <text class="cf-empty__text">{{ text }}</text>
    <slot />
  </view>
</template>

<script setup lang="ts">
import CfIcon from './CfIcon.vue'

defineProps<{
  icon?: string
  text?: string
}>()
</script>

<style lang="scss" scoped>
.cf-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx $sp-lg;
  gap: $sp-sm;

  &__text {
    font-size: 26rpx;
    color: $cf-text-3;
  }
}
</style>
