import { http } from "./client";
import type { MembershipTier } from "../types";

export async function listMembershipTiers(): Promise<MembershipTier[]> {
  return http.get<MembershipTier[]>("/api/v1/admin/membership-tiers");
}

export async function getMembershipTier(
  id: string,
): Promise<MembershipTier> {
  return http.get<MembershipTier>(`/api/v1/admin/membership-tiers/${id}`);
}

export async function createMembershipTier(
  data: Partial<MembershipTier>,
): Promise<MembershipTier> {
  return http.post<MembershipTier>(
    "/api/v1/admin/membership-tiers",
    data as Record<string, unknown>,
  );
}

export async function updateMembershipTier(
  id: string,
  data: Partial<MembershipTier>,
): Promise<MembershipTier> {
  return http.put<MembershipTier>(
    `/api/v1/admin/membership-tiers/${id}`,
    data as Record<string, unknown>,
  );
}

export async function deleteMembershipTier(id: string): Promise<void> {
  return http.del(`/api/v1/admin/membership-tiers/${id}`);
}
