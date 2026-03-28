<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">会员方案</text>
      <CfButton type="primary" size="sm" icon="plus" @click="goCreate">新建</CfButton>
    </view>

    <scroll-view scroll-y class="content">
      <CfEmpty v-if="!tiers.length" icon="ticket" text="暂无会员方案" />
      <view
        v-for="tier in tiers"
        :key="tier.id"
        class="tier-card cf-glass-card"
        @click="goEdit(tier.id)"
      >
        <view class="tier-card__top">
          <text class="tier-card__name">{{ tier.name }}</text>
          <view :class="['cf-badge', tier.is_active ? 'cf-badge--lime' : 'cf-badge--grey']">
            {{ tier.is_active ? '在售' : '停售' }}
          </view>
        </view>
        <view class="tier-card__price">
          <text class="tier-card__amount">¥{{ (tier.price_cents / 100).toFixed(0) }}</text>
          <text class="tier-card__duration">/ {{ tier.duration_days }}天</text>
        </view>
        <view class="tier-card__meta">
          <text class="tier-card__tag">{{ scopeLabel(tier.scope) }}</text>
          <text v-if="tier.price_discount_pct" class="tier-card__tag">
            {{ tier.price_discount_pct }}% 折扣
          </text>
          <text v-if="tier.monthly_hour_quota" class="tier-card__tag">
            {{ tier.monthly_hour_quota }}h/月
          </text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfButton from '@/components/ui/CfButton.vue'
import CfEmpty from '@/components/ui/CfEmpty.vue'
import type { MembershipTier } from '@/types'
import { listMembershipTiers } from '@/api/memberships'

const tiers = ref<MembershipTier[]>([])

const scopeLabels: Record<string, string> = {
  organization: '全机构', venue: '场馆级', court_type: '场地类型', court: '单场地',
}
function scopeLabel(s: string) { return scopeLabels[s] ?? s }

onShow(async () => {
  try { tiers.value = await listMembershipTiers() } catch {}
})

function goCreate() {
  uni.navigateTo({ url: '/packages/membership/edit/index' })
}

function goEdit(id: string) {
  uni.navigateTo({ url: `/packages/membership/edit/index?id=${id}` })
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

.tier-card {
  padding: $sp-md;
  margin-bottom: $sp-sm;

  &__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8rpx;
  }

  &__name { font-size: 28rpx; font-weight: 700; color: $cf-white; }

  &__price {
    display: flex;
    align-items: baseline;
    gap: 6rpx;
    margin-bottom: 12rpx;
  }

  &__amount { font-size: 40rpx; font-weight: 800; color: $cf-lime; }
  &__duration { font-size: 24rpx; color: $cf-text-2; }

  &__meta { display: flex; flex-wrap: wrap; gap: 8rpx; }

  &__tag {
    font-size: 22rpx;
    color: $cf-text-2;
    background: $cf-glass-bg;
    padding: 4rpx 12rpx;
    border-radius: $r-full;
  }
}
</style>
