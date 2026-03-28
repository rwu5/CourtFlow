import { defineStore } from "pinia";
import { ref } from "vue";
import type { Organization, DashboardStats } from "../types";
import { getMyOrganization, getDashboardStats } from "../api/organizations";

export const useOrgStore = defineStore("org", () => {
  const organization = ref<Organization | null>(null);
  const stats = ref<DashboardStats | null>(null);

  async function fetchOrganization() {
    organization.value = await getMyOrganization();
  }

  async function fetchStats() {
    stats.value = await getDashboardStats();
  }

  async function init() {
    await Promise.all([fetchOrganization(), fetchStats()]);
  }

  return {
    organization,
    stats,
    fetchOrganization,
    fetchStats,
    init,
  };
});
