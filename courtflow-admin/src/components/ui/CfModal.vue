<template>
  <view v-if="visible" class="cf-modal" @click.self="handleMaskClick">
    <view class="cf-modal__card cf-glass-card">
      <view class="cf-modal__header">
        <text class="cf-modal__title">{{ title }}</text>
        <view class="cf-modal__close" @click="emit('close')">
          <CfIcon name="close" :size="20" color="rgba(255,255,255,0.5)" />
        </view>
      </view>
      <view class="cf-modal__body">
        <slot />
      </view>
      <view v-if="showFooter" class="cf-modal__footer">
        <CfButton type="secondary" size="md" @click="emit('close')">取消</CfButton>
        <CfButton :type="confirmType" size="md" @click="emit('confirm')">
          {{ confirmText }}
        </CfButton>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import CfIcon from './CfIcon.vue'
import CfButton from './CfButton.vue'

const props = defineProps<{
  visible: boolean
  title: string
  confirmText?: string
  confirmType?: 'primary' | 'danger'
  showFooter?: boolean
  maskClose?: boolean
}>()

const emit = defineEmits<{
  close: []
  confirm: []
}>()

function handleMaskClick() {
  if (props.maskClose !== false) emit('close')
}
</script>

<style lang="scss" scoped>
.cf-modal {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  padding: $sp-lg;

  &__card {
    width: 100%;
    max-width: 600rpx;
    padding: $sp-md;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: $sp-md;
  }

  &__title {
    font-size: 32rpx;
    font-weight: 700;
    color: $cf-white;
  }

  &__close {
    padding: 8rpx;
  }

  &__body {
    margin-bottom: $sp-md;
    color: $cf-text-2;
    font-size: 28rpx;
    line-height: 1.6;
  }

  &__footer {
    display: flex;
    gap: $sp-sm;
    justify-content: flex-end;
  }
}
</style>
