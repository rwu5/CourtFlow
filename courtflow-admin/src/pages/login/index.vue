<template>
  <view class="cf-page login-page">
    <view class="login-page__content">
      <text class="login-page__title">CourtFlow</text>
      <text class="login-page__subtitle">机构管理后台</text>

      <view class="login-form">
        <CfFormItem label="手机号" required>
          <input
            v-model="phone"
            type="number"
            placeholder="请输入手机号"
            maxlength="11"
            class="login-input"
          />
        </CfFormItem>

        <CfFormItem label="验证码" required>
          <view class="code-row">
            <input
              v-model="code"
              type="number"
              placeholder="请输入验证码"
              maxlength="6"
              class="login-input code-input"
            />
            <CfButton
              type="secondary"
              size="sm"
              :disabled="codeCooldown > 0"
              @click="sendCode"
            >
              {{ codeCooldown > 0 ? `${codeCooldown}s` : '获取验证码' }}
            </CfButton>
          </view>
        </CfFormItem>

        <CfButton
          type="primary"
          size="lg"
          block
          :disabled="!canLogin"
          @click="handleLogin"
        >
          登录
        </CfButton>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CfFormItem from '@/components/ui/CfFormItem.vue'
import CfButton from '@/components/ui/CfButton.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const phone = ref('')
const code = ref('')
const codeCooldown = ref(0)

const canLogin = computed(() => phone.value.length === 11 && code.value.length >= 4)

function sendCode() {
  if (phone.value.length !== 11) {
    uni.showToast({ title: '请输入正确手机号', icon: 'none' })
    return
  }
  // TODO: call SMS API
  codeCooldown.value = 60
  const timer = setInterval(() => {
    codeCooldown.value--
    if (codeCooldown.value <= 0) clearInterval(timer)
  }, 1000)
  uni.showToast({ title: '验证码已发送', icon: 'none' })
}

async function handleLogin() {
  try {
    await authStore.login(phone.value, code.value)
    uni.switchTab({ url: '/pages/index/index' })
  } catch (e: any) {
    uni.showToast({ title: e.detail ?? '登录失败', icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;

  &__content {
    width: 100%;
    padding: 0 64rpx;
  }

  &__title {
    font-size: 56rpx;
    font-weight: 900;
    color: $cf-white;
    text-align: center;
    display: block;
  }

  &__subtitle {
    font-size: 28rpx;
    color: $cf-text-2;
    text-align: center;
    margin-bottom: 80rpx;
    display: block;
  }
}

.login-form {
  margin-top: 40rpx;
}

.login-input {
  width: 100%;
  background: $cf-glass-bg;
  border: 0.5px solid $cf-glass-border;
  border-radius: $r-md;
  padding: 20rpx 24rpx;
  color: $cf-white;
  font-size: 28rpx;
}

.code-row {
  display: flex;
  gap: $sp-sm;
  align-items: center;
}

.code-input {
  flex: 1;
}
</style>
