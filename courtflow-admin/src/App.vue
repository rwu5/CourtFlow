<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { useAuthStore } from "@/stores/auth";

onLaunch(async () => {
  console.log("CourtFlow Admin Launch");
  const authStore = useAuthStore();
  await authStore.init();
});
onShow(() => {
  console.log("App Show");
});
onHide(() => {
  console.log("App Hide");
});
</script>
<style></style>
