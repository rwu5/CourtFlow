<template>
  <view class="cf-page">
    <view class="page-header">
      <text class="page-header__title">我的</text>
    </view>

    <scroll-view scroll-y class="content">
      <!-- Profile Card -->
      <view class="profile-card cf-glass-card">
        <view class="profile-card__avatar-wrap">
          <image
            v-if="user?.avatar_url"
            :src="user.avatar_url"
            class="profile-card__avatar"
            mode="aspectFill"
          />
          <view v-else class="profile-card__avatar profile-card__avatar--placeholder">
            <CfIcon name="person" :size="32" color="rgba(255,255,255,0.3)" />
          </view>
        </view>
        <view class="profile-card__info">
          <text class="profile-card__name">{{ user?.nickname ?? '未设置昵称' }}</text>
          <text class="profile-card__phone">{{ user?.phone ?? '' }}</text>
        </view>
      </view>

      <!-- Menu Items -->
      <CfCard>
        <view
          v-for="item in menuItems"
          :key="item.label"
          class="menu-item"
          @click="item.action"
        >
          <view class="menu-item__left">
            <CfIcon :name="item.icon" :size="20" :color="item.color" />
            <text class="menu-item__label">{{ item.label }}</text>
          </view>
          <CfIcon name="chevron-right" :size="16" color="rgba(255,255,255,0.2)" />
        </view>
      </CfCard>

      <!-- Logout -->
      <view style="padding: 32rpx 0">
        <CfButton type="danger" block size="md" @click="handleLogout">退出登录</CfButton>
      </view>
    </scroll-view>

    <CfTabBar current="pages/my/index" />
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfCard from '@/components/ui/CfCard.vue'
import CfButton from '@/components/ui/CfButton.vue'
import CfTabBar from '@/components/ui/CfTabBar.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const menuItems = [
  {
    icon: 'building',
    color: '#34d399',
    label: '机构信息',
    action: () => uni.navigateTo({ url: '/packages/org/profile/index' }),
  },
  {
    icon: 'ticket',
    color: '#B8D430',
    label: '会员方案',
    action: () => uni.navigateTo({ url: '/packages/membership/list/index' }),
  },
  {
    icon: 'shield',
    color: '#2E86C1',
    label: '权限管理',
    action: () => uni.showToast({ title: '即将上线', icon: 'none' }),
  },
  {
    icon: 'settings',
    color: '#c084fc',
    label: '系统设置',
    action: () => uni.showToast({ title: '即将上线', icon: 'none' }),
  },
]

function handleLogout() {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success(res) {
      if (res.confirm) authStore.logout()
    },
  })
}
</script>

<style lang="scss" scoped>
.page-header {
  padding: 24rpx 32rpx;
  padding-top: calc(env(safe-area-inset-top) + 24rpx);

  &__title {
    font-size: 36rpx;
    font-weight: 800;
    color: $cf-white;
  }
}

.content {
  height: calc(100vh - 160rpx - env(safe-area-inset-top) - 100rpx);
  padding: 0 $sp-md;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: $sp-md;
  margin-bottom: $sp-sm;

  &__avatar-wrap {
    flex-shrink: 0;
  }

  &__avatar {
    width: 100rpx;
    height: 100rpx;
    border-radius: 50%;

    &--placeholder {
      display: flex;
      align-items: center;
      justify-content: center;
      background: $cf-glass-bg;
      border: 0.5px solid $cf-glass-border;
    }
  }

  &__info {
    display: flex;
    flex-direction: column;
    gap: 6rpx;
  }

  &__name {
    font-size: 32rpx;
    font-weight: 700;
    color: $cf-white;
  }

  &__phone {
    font-size: 24rpx;
    color: $cf-text-2;
  }
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 0;
  border-bottom: 0.5px solid $cf-line;

  &:last-child {
    border-bottom: none;
  }

  &__left {
    display: flex;
    align-items: center;
    gap: 16rpx;
  }

  &__label {
    font-size: 28rpx;
    color: $cf-white;
  }
}
</style>
