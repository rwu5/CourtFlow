import { http } from "./client";
import type { VenueListItem, VenueDetail, AvailabilityGrid } from "../types";

export async function listVenues(params?: {
  is_partner?: boolean;
  city?: string;
}): Promise<VenueListItem[]> {
  const p: Record<string, string | number | boolean> = {};
  if (params?.is_partner !== undefined) p["is_partner"] = params.is_partner;
  if (params?.city) p["city"] = params.city;
  return http.get<VenueListItem[]>("/api/v1/venues", p, false);
}

export async function getVenue(id: string): Promise<VenueDetail> {
  return http.get<VenueDetail>(`/api/v1/venues/${id}`, undefined, false);
}

export async function getAvailability(
  venueId: string,
  date: string,
): Promise<AvailabilityGrid> {
  return http.get<AvailabilityGrid>(`/api/v1/venues/${venueId}/availability`, {
    date,
  });
}
