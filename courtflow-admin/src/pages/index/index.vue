<template>
  <view class="cf-page">
    <!-- Header -->
    <view class="header">
      <view class="header__left">
        <image
          v-if="org?.logo_url"
          :src="org.logo_url"
          class="header__logo"
          mode="aspectFill"
        />
        <view class="header__info">
          <text class="header__org-name">{{ org?.name ?? '加载中...' }}</text>
          <text class="header__sub">管理后台</text>
        </view>
      </view>
      <view class="header__right" @click="uni.navigateTo({ url: '/packages/org/profile/index' })">
        <CfIcon name="settings" :size="22" color="rgba(255,255,255,0.5)" />
      </view>
    </view>

    <scroll-view scroll-y class="content">
      <!-- Stats Grid -->
      <view class="stats-grid">
        <view class="stat-card cf-glass-card" v-for="item in statCards" :key="item.label">
          <text class="stat-card__value">{{ item.value }}</text>
          <text class="stat-card__label">{{ item.label }}</text>
        </view>
      </view>

      <!-- Quick Actions -->
      <CfCard title="快捷操作">
        <view class="actions-grid">
          <view
            v-for="action in quickActions"
            :key="action.label"
            class="action-item"
            @click="uni.navigateTo({ url: action.path })"
          >
            <view class="action-item__icon" :style="{ background: action.bg }">
              <CfIcon :name="action.icon" :size="20" :color="action.color" />
            </view>
            <text class="action-item__label">{{ action.label }}</text>
          </view>
        </view>
      </CfCard>
    </scroll-view>

    <CfTabBar current="pages/index/index" />
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfCard from '@/components/ui/CfCard.vue'
import CfTabBar from '@/components/ui/CfTabBar.vue'
import { useOrgStore } from '@/stores/org'

const orgStore = useOrgStore()
const org = computed(() => orgStore.organization)
const stats = computed(() => orgStore.stats)

const statCards = computed(() => [
  { label: '场馆', value: stats.value?.total_venues ?? '-' },
  { label: '场地', value: stats.value?.total_courts ?? '-' },
  { label: '会员', value: stats.value?.total_members ?? '-' },
  { label: '定价规则', value: stats.value?.active_pricing_rules ?? '-' },
])

const quickActions = [
  { label: '新建场馆', icon: 'plus', path: '/packages/venue/edit/index', bg: 'rgba(45,139,87,0.18)', color: '#34d399' },
  { label: '定价管理', icon: 'money', path: '/pages/pricing/index', bg: 'rgba(46,134,193,0.18)', color: '#2E86C1' },
  { label: '会员方案', icon: 'ticket', path: '/packages/membership/list/index', bg: 'rgba(184,212,48,0.14)', color: '#B8D430' },
  { label: '机构信息', icon: 'building', path: '/packages/org/profile/index', bg: 'rgba(123,79,160,0.16)', color: '#c084fc' },
]

onMounted(() => {
  orgStore.init()
})
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  padding-top: calc(env(safe-area-inset-top) + 24rpx);

  &__left {
    display: flex;
    align-items: center;
    gap: 16rpx;
  }

  &__logo {
    width: 72rpx;
    height: 72rpx;
    border-radius: $r-md;
  }

  &__org-name {
    font-size: 34rpx;
    font-weight: 700;
    color: $cf-white;
  }

  &__sub {
    font-size: 22rpx;
    color: $cf-text-2;
  }

  &__info {
    display: flex;
    flex-direction: column;
    gap: 4rpx;
  }

  &__right {
    padding: 16rpx;
  }
}

.content {
  height: calc(100vh - 200rpx - env(safe-area-inset-top) - 100rpx);
  padding: 0 $sp-md;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $sp-sm;
  margin-bottom: $sp-md;
}

.stat-card {
  padding: $sp-md;
  display: flex;
  flex-direction: column;
  gap: 8rpx;

  &__value {
    font-size: 48rpx;
    font-weight: 800;
    color: $cf-white;
  }

  &__label {
    font-size: 24rpx;
    color: $cf-text-2;
  }
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $sp-sm;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;

  &__icon {
    width: 88rpx;
    height: 88rpx;
    border-radius: $r-lg;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__label {
    font-size: 22rpx;
    color: $cf-text-2;
  }
}
</style>
