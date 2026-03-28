<template>
  <view class="cf-page">
    <view class="page-header">
      <view class="page-header__back" @click="uni.navigateBack()">
        <CfIcon name="chevron-left" :size="22" />
      </view>
      <text class="page-header__title">机构信息</text>
      <view style="width: 44rpx" />
    </view>

    <scroll-view scroll-y class="content">
      <CfFormItem label="机构名称" required>
        <input v-model="form.name" placeholder="输入机构名称" />
      </CfFormItem>

      <CfFormItem label="机构简称">
        <input v-model="form.slug" placeholder="英文标识 (URL 使用)" />
      </CfFormItem>

      <CfFormItem label="机构描述">
        <textarea v-model="form.description" placeholder="介绍你的机构" />
      </CfFormItem>

      <CfFormItem label="机构 Logo">
        <CfImageUpload v-model="logoList" :max="1" />
      </CfFormItem>

      <view style="padding-top: 24rpx">
        <CfButton type="primary" size="lg" block :disabled="saving" @click="handleSave">
          {{ saving ? '保存中...' : '保存' }}
        </CfButton>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'
import CfFormItem from '@/components/ui/CfFormItem.vue'
import CfImageUpload from '@/components/ui/CfImageUpload.vue'
import CfButton from '@/components/ui/CfButton.vue'
import { useOrgStore } from '@/stores/org'
import { updateOrganization } from '@/api/organizations'

const orgStore = useOrgStore()
const saving = ref(false)

const form = ref({
  name: '',
  slug: '',
  description: '',
})

const logoList = ref<string[]>([])

onMounted(() => {
  const org = orgStore.organization
  if (org) {
    form.value.name = org.name
    form.value.slug = org.slug
    form.value.description = org.description ?? ''
    if (org.logo_url) logoList.value = [org.logo_url]
  }
})

async function handleSave() {
  if (!form.value.name) {
    uni.showToast({ title: '请输入机构名称', icon: 'none' })
    return
  }
  saving.value = true
  try {
    await updateOrganization({
      name: form.value.name,
      slug: form.value.slug,
      description: form.value.description || null,
      logo_url: logoList.value[0] || null,
    } as any)
    await orgStore.fetchOrganization()
    uni.showToast({ title: '保存成功' })
    uni.navigateBack()
  } catch (e: any) {
    uni.showToast({ title: e.detail ?? '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  padding-top: calc(env(safe-area-inset-top) + 24rpx);

  &__back {
    padding: 8rpx;
  }

  &__title {
    font-size: 32rpx;
    font-weight: 700;
    color: $cf-white;
  }
}

.content {
  padding: $sp-md;
  height: calc(100vh - 160rpx - env(safe-area-inset-top));
}
</style>
