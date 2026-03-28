import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User } from "../types";
import { loginWithPhone, getMe } from "../api/auth";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(
    uni.getStorageSync("access_token") || null,
  );

  const isLoggedIn = computed(() => !!accessToken.value && !!user.value);

  function saveTokens(access: string, refresh: string) {
    accessToken.value = access;
    uni.setStorageSync("access_token", access);
    uni.setStorageSync("refresh_token", refresh);
  }

  async function login(phone: string, code: string) {
    const tokens = await loginWithPhone(phone, code);
    saveTokens(tokens.access_token, tokens.refresh_token);
    await fetchMe();
  }

  async function fetchMe() {
    user.value = await getMe();
  }

  function logout() {
    user.value = null;
    accessToken.value = null;
    uni.removeStorageSync("access_token");
    uni.removeStorageSync("refresh_token");
    uni.reLaunch({ url: "/pages/login/index" });
  }

  async function init() {
    if (accessToken.value) {
      try {
        await fetchMe();
      } catch {
        logout();
      }
    }
  }

  return {
    user,
    accessToken,
    isLoggedIn,
    login,
    fetchMe,
    logout,
    init,
  };
});
