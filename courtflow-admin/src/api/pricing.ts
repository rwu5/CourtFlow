import { http } from "./client";
import type { PricingRule } from "../types";

export async function listPricingRules(params?: {
  venue_id?: string;
  court_id?: string;
  court_type_id?: string;
}): Promise<PricingRule[]> {
  const p: Record<string, string | number | boolean> = {};
  if (params?.venue_id) p["venue_id"] = params.venue_id;
  if (params?.court_id) p["court_id"] = params.court_id;
  if (params?.court_type_id) p["court_type_id"] = params.court_type_id;
  return http.get<PricingRule[]>("/api/v1/admin/pricing-rules", p);
}

export async function getPricingRule(id: string): Promise<PricingRule> {
  return http.get<PricingRule>(`/api/v1/admin/pricing-rules/${id}`);
}

export async function createPricingRule(
  data: Partial<PricingRule>,
): Promise<PricingRule> {
  return http.post<PricingRule>(
    "/api/v1/admin/pricing-rules",
    data as Record<string, unknown>,
  );
}

export async function updatePricingRule(
  id: string,
  data: Partial<PricingRule>,
): Promise<PricingRule> {
  return http.put<PricingRule>(
    `/api/v1/admin/pricing-rules/${id}`,
    data as Record<string, unknown>,
  );
}

export async function deletePricingRule(id: string): Promise<void> {
  return http.del(`/api/v1/admin/pricing-rules/${id}`);
}
