<template>
  <view
    class="cf-button"
    :class="[
      `cf-button--${type}`,
      `cf-button--${size}`,
      { 'cf-button--block': block, 'cf-button--disabled': disabled },
    ]"
    @click="handleClick"
  >
    <CfIcon v-if="icon" :name="icon" :size="iconSize" />
    <text v-if="$slots.default" class="cf-button__text"><slot /></text>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CfIcon from './CfIcon.vue'

const props = defineProps<{
  type?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  icon?: string
  block?: boolean
  disabled?: boolean
}>()

const emit = defineEmits<{ click: [] }>()

const iconSize = computed(() => {
  const s = props.size ?? 'md'
  return s === 'sm' ? 16 : s === 'lg' ? 22 : 18
})

function handleClick() {
  if (!props.disabled) emit('click')
}
</script>

<style lang="scss" scoped>
.cf-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  border-radius: $r-full;
  font-weight: 600;
  transition: opacity 0.15s;

  &:active:not(.cf-button--disabled) {
    opacity: 0.8;
  }

  &--disabled {
    opacity: 0.4;
    pointer-events: none;
  }

  &--block {
    display: flex;
    width: 100%;
  }

  // Types
  &--primary {
    background: linear-gradient(135deg, $cf-green 0%, $cf-blue 100%);
    color: #fff;
    box-shadow: 0 8rpx 32rpx $cf-green-glow;
  }

  &--secondary {
    background: $cf-glass-bg;
    border: 0.5px solid $cf-glass-border;
    color: $cf-white;
  }

  &--danger {
    background: rgba(240, 69, 69, 0.15);
    border: 0.5px solid rgba(240, 69, 69, 0.3);
    color: $cf-danger;
  }

  &--ghost {
    background: transparent;
    color: $cf-text-2;
  }

  // Sizes
  &--sm {
    height: 56rpx;
    padding: 0 24rpx;
    font-size: 24rpx;
  }

  &--md {
    height: 72rpx;
    padding: 0 32rpx;
    font-size: 28rpx;
  }

  &--lg {
    height: 96rpx;
    padding: 0 48rpx;
    font-size: 30rpx;
  }

  &__text {
    line-height: 1;
  }
}
</style>
