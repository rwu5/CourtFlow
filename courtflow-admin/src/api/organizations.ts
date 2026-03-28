import { http } from "./client";
import type { Organization, OrganizationMember, DashboardStats } from "../types";

export async function getMyOrganization(): Promise<Organization> {
  return http.get<Organization>("/api/v1/admin/organization");
}

export async function updateOrganization(
  data: Partial<Organization>,
): Promise<Organization> {
  return http.put<Organization>(
    "/api/v1/admin/organization",
    data as Record<string, unknown>,
  );
}

export async function listMembers(): Promise<OrganizationMember[]> {
  return http.get<OrganizationMember[]>("/api/v1/admin/organization/members");
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return http.get<DashboardStats>("/api/v1/admin/dashboard/stats");
}
