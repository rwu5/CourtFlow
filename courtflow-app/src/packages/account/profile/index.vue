<template>
  <view class="profile">
    <view class="profile__nav">
      <view class="profile__back" @tap="goBack">
        <cf-icon name="chevron-left" :size="22" color="rgba(255,255,255,0.85)" />
      </view>
      <text class="profile__nav-title">个人信息</text>
      <view class="profile__save-btn" :class="{ 'profile__save-btn--active': hasChanges }" @tap="save">
        <text class="profile__save-text">保存</text>
      </view>
    </view>

    <scroll-view class="profile__scroll" scroll-y>
      <!-- Avatar section -->
      <view class="profile__avatar-section">
        <view class="profile__avatar-wrap" @tap="chooseAvatar">
          <image class="profile__avatar" :src="form.avatar || '/static/default-avatar.png'" mode="aspectFill" />
          <view class="profile__avatar-edit">
            <cf-icon name="edit" :size="18" color="rgba(255,255,255,0.8)" />
          </view>
        </view>
        <text class="profile__avatar-hint">点击更换头像</text>
      </view>

      <!-- Basic info -->
      <view class="profile__section">
        <text class="profile__section-title">基本信息</text>
        <view class="profile__field">
          <text class="profile__field-label">昵称</text>
          <input
            v-model="form.nickname"
            class="profile__field-input"
            placeholder="请输入昵称"
            placeholder-class="profile__field-placeholder"
            @input="onFormChange"
          />
        </view>
        <view class="profile__field-divider" />
        <view class="profile__field">
          <text class="profile__field-label">手机号</text>
          <text class="profile__field-value profile__field-value--phone">{{ form.phone || '未绑定' }}</text>
          <text class="profile__field-action">更换 ›</text>
        </view>
        <view class="profile__field-divider" />
        <view class="profile__field">
          <text class="profile__field-label">性别</text>
          <view class="profile__gender-row">
            <view
              v-for="g in genders"
              :key="g.value"
              class="profile__gender-btn"
              :class="{ 'profile__gender-btn--active': form.gender === g.value }"
              @tap="form.gender = g.value; onFormChange()"
            >
              <text class="profile__gender-text">{{ g.label }}</text>
            </view>
          </view>
        </view>
        <view class="profile__field-divider" />
        <view class="profile__field">
          <text class="profile__field-label">个性签名</text>
          <input
            v-model="form.bio"
            class="profile__field-input"
            placeholder="来一句网球座右铭吧"
            placeholder-class="profile__field-placeholder"
            @input="onFormChange"
          />
        </view>
      </view>

      <!-- Tennis profile -->
      <view class="profile__section">
        <text class="profile__section-title">网球档案</text>

        <view class="profile__field">
          <text class="profile__field-label">技术水平</text>
        </view>
        <view class="profile__levels-grid">
          <view
            v-for="lv in levels"
            :key="lv.value"
            class="profile__level-card"
            :class="{ 'profile__level-card--active': form.playerLevel === lv.value }"
            @tap="form.playerLevel = lv.value; onFormChange()"
          >
            <view class="profile__level-pips">
              <view
                v-for="n in 5"
                :key="n"
                class="profile__level-pip"
                :class="{ 'profile__level-pip--on': n <= lv.rank }"
              />
            </view>
            <text class="profile__level-label">{{ lv.label }}</text>
            <text class="profile__level-desc">{{ lv.desc }}</text>
          </view>
        </view>

        <view class="profile__field-divider" />
        <view class="profile__field">
          <text class="profile__field-label">持拍手</text>
          <view class="profile__hand-row">
            <view
              v-for="h in hands"
              :key="h.value"
              class="profile__hand-btn"
              :class="{ 'profile__hand-btn--active': form.dominantHand === h.value }"
              @tap="form.dominantHand = h.value; onFormChange()"
            >
              <text class="profile__hand-text">{{ h.label }}</text>
            </view>
          </view>
        </view>

        <view class="profile__field-divider" />
        <view class="profile__field">
          <text class="profile__field-label">反手类型</text>
          <view class="profile__hand-row">
            <view
              v-for="b in backhands"
              :key="b.value"
              class="profile__hand-btn"
              :class="{ 'profile__hand-btn--active': form.backhandType === b.value }"
              @tap="form.backhandType = b.value; onFormChange()"
            >
              <text class="profile__hand-text">{{ b.label }}</text>
            </view>
          </view>
        </view>
      </view>

      <view style="height: 60rpx;" />
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CfIcon from '@/components/ui/CfIcon.vue'

const hasChanges = ref(false)

const form = ref({
  avatar: '',
  nickname: '网球爱好者',
  phone: '138****8888',
  gender: 'male',
  bio: '',
  playerLevel: 'intermediate',
  dominantHand: 'right',
  backhandType: 'two_handed',
})

const genders = [
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'other', label: '其他' },
]

const levels = [
  { value: 'beginner',     rank: 1, label: '入门', desc: '刚开始学习' },
  { value: 'elementary',   rank: 2, label: '初级', desc: '掌握基础' },
  { value: 'intermediate', rank: 3, label: '中级', desc: '稳定对打' },
  { value: 'advanced',     rank: 4, label: '高级', desc: '参加比赛' },
  { value: 'professional', rank: 5, label: '专业', desc: '职业水平' },
]

const hands = [
  { value: 'right', label: '右手' },
  { value: 'left', label: '左手' },
]

const backhands = [
  { value: 'two_handed', label: '双手反拍' },
  { value: 'one_handed', label: '单手反拍' },
]

function onFormChange() {
  hasChanges.value = true
}

async function chooseAvatar() {
  try {
    const res = await uni.chooseImage({ count: 1, sizeType: ['compressed'] })
    form.value.avatar = res.tempFilePaths[0]
    hasChanges.value = true
  } catch {}
}

async function save() {
  if (!hasChanges.value) return
  try {
    // TODO: call API
    uni.showToast({ title: '保存成功', icon: 'success' })
    hasChanges.value = false
  } catch {
    uni.showToast({ title: '保存失败，请重试', icon: 'none' })
  }
}

function goBack() {
  uni.navigateBack()
}
</script>

<style lang="scss">
@import '@/uni.scss';

.profile {
  background: $cf-bg;
  min-height: 100vh;
}

// ─── Nav ─────────────────────────────────────────────────────────────────────
.profile__nav {
  display: flex;
  align-items: center;
  padding: 0 24rpx;
  height: 88rpx;
  background: $cf-surface;
  border-bottom: 1rpx solid $cf-line;
}

.profile__back {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $cf-card;
  border-radius: $r-full;
  border: 1rpx solid $cf-line;
}

.profile__back-icon {
  font-size: 44rpx;
  color: $cf-white;
  font-weight: 300;
}

.profile__nav-title {
  flex: 1;
  text-align: center;
  font-size: 30rpx;
  font-weight: 700;
  color: $cf-white;
}

.profile__save-btn {
  padding: 10rpx 24rpx;
  border-radius: $r-full;
  border: 1rpx solid $cf-line;
  background: $cf-card;
  &--active { background: $cf-accent; border-color: $cf-accent; }
}

.profile__save-text {
  font-size: 24rpx;
  font-weight: 600;
  color: $cf-text-2;
  .profile__save-btn--active & { color: #0a1a0d; }
}

.profile__scroll {
  height: calc(100vh - 88rpx);
}

// ─── Avatar ──────────────────────────────────────────────────────────────────
.profile__avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48rpx 0 32rpx;
}

.profile__avatar-wrap {
  position: relative;
  width: 160rpx;
  height: 160rpx;
  margin-bottom: 16rpx;
}

.profile__avatar {
  width: 160rpx;
  height: 160rpx;
  border-radius: $r-full;
  border: 3rpx solid $cf-accent;
  background: $cf-card;
}

.profile__avatar-edit {
  position: absolute;
  bottom: 4rpx;
  right: 4rpx;
  width: 48rpx;
  height: 48rpx;
  background: $cf-card-2;
  border-radius: $r-full;
  border: 2rpx solid $cf-line-2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile__avatar-edit-icon {
  font-size: 24rpx;
}

.profile__avatar-hint {
  font-size: 22rpx;
  color: $cf-text-3;
}

// ─── Section ─────────────────────────────────────────────────────────────────
.profile__section {
  margin: 0 32rpx 16rpx;
  background: $cf-card;
  border-radius: $r-xl;
  padding: 24rpx 28rpx;
  border: 1rpx solid $cf-line;
}

.profile__section-title {
  font-size: 22rpx;
  font-weight: 700;
  color: $cf-text-2;
  letter-spacing: 0.06em;
  display: block;
  margin-bottom: 20rpx;
}

// ─── Fields ──────────────────────────────────────────────────────────────────
.profile__field {
  display: flex;
  align-items: center;
  min-height: 72rpx;
  gap: 16rpx;
}

.profile__field-label {
  font-size: 26rpx;
  color: $cf-white;
  font-weight: 500;
  width: 120rpx;
  flex-shrink: 0;
}

.profile__field-input {
  flex: 1;
  font-size: 26rpx;
  color: $cf-white;
  background: transparent;
  text-align: right;
}

.profile__field-placeholder {
  color: $cf-text-3;
  font-size: 26rpx;
}

.profile__field-value {
  flex: 1;
  font-size: 26rpx;
  color: $cf-text-2;
  text-align: right;
  &--phone { color: $cf-white; }
}

.profile__field-action {
  font-size: 24rpx;
  color: $cf-accent;
  font-weight: 500;
  flex-shrink: 0;
}

.profile__field-divider {
  height: 1rpx;
  background: $cf-line;
  margin: 4rpx 0;
}

// ─── Gender ──────────────────────────────────────────────────────────────────
.profile__gender-row {
  display: flex;
  gap: 12rpx;
  flex: 1;
  justify-content: flex-end;
}

.profile__gender-btn {
  padding: 8rpx 24rpx;
  border-radius: $r-full;
  background: $cf-card-2;
  border: 1rpx solid $cf-line;
  &--active { background: $cf-accent-dim; border-color: rgba(196,232,74,0.4); }
}

.profile__gender-text {
  font-size: 22rpx;
  color: $cf-text-2;
  .profile__gender-btn--active & { color: $cf-accent; font-weight: 600; }
}

// ─── Level cards ─────────────────────────────────────────────────────────────
.profile__levels-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.profile__level-card {
  background: $cf-card-2;
  border-radius: $r-md;
  padding: 16rpx 8rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  border: 1rpx solid $cf-line;
  &--active { background: $cf-accent-dim; border-color: rgba(196,232,74,0.4); }
}

.profile__level-pips {
  display: flex;
  gap: 4rpx;
  margin-bottom: 4rpx;
}
.profile__level-pip {
  width: 10rpx;
  height: 10rpx;
  border-radius: 3rpx;
  background: $cf-line-2;
  &--on { background: $cf-lime; box-shadow: 0 0 6rpx rgba(184,212,48,0.5); }
  .profile__level-card--active & { &--on { background: $cf-lime; } }
}

.profile__level-label {
  font-size: 20rpx;
  font-weight: 700;
  color: $cf-white;
  .profile__level-card--active & { color: $cf-accent; }
}

.profile__level-desc {
  font-size: 16rpx;
  color: $cf-text-3;
  text-align: center;
}

// ─── Hand / Backhand ─────────────────────────────────────────────────────────
.profile__hand-row {
  display: flex;
  gap: 12rpx;
  flex: 1;
  justify-content: flex-end;
}

.profile__hand-btn {
  padding: 8rpx 28rpx;
  border-radius: $r-full;
  background: $cf-card-2;
  border: 1rpx solid $cf-line;
  &--active { background: $cf-accent-dim; border-color: rgba(196,232,74,0.4); }
}

.profile__hand-text {
  font-size: 22rpx;
  color: $cf-text-2;
  .profile__hand-btn--active & { color: $cf-accent; font-weight: 600; }
}
</style>
