<template>
  <view class="cf-glass-card cf-card" :style="customStyle">
    <view v-if="title" class="cf-card__header">
      <text class="cf-card__title">{{ title }}</text>
      <slot name="action" />
    </view>
    <slot />
  </view>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  customStyle?: string
}>()
</script>

<style lang="scss" scoped>
.cf-card {
  padding: $sp-md;
  margin-bottom: $sp-sm;

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: $sp-sm;
  }

  &__title {
    font-size: 30rpx;
    font-weight: 700;
    color: $cf-white;
  }
}
</style>
