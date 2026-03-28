import { http } from "./client";
import type { Venue, VenueMedia, VenueFacility } from "../types";

export async function listVenues(): Promise<Venue[]> {
  return http.get<Venue[]>("/api/v1/admin/venues");
}

export async function getVenue(id: string): Promise<Venue> {
  return http.get<Venue>(`/api/v1/admin/venues/${id}`);
}

export async function createVenue(
  data: Partial<Venue>,
): Promise<Venue> {
  return http.post<Venue>(
    "/api/v1/admin/venues",
    data as Record<string, unknown>,
  );
}

export async function updateVenue(
  id: string,
  data: Partial<Venue>,
): Promise<Venue> {
  return http.put<Venue>(
    `/api/v1/admin/venues/${id}`,
    data as Record<string, unknown>,
  );
}

export async function deleteVenue(id: string): Promise<void> {
  return http.del(`/api/v1/admin/venues/${id}`);
}

// ─── Media ───────────────────────────────────────────────────────────────────
export async function listVenueMedia(
  venueId: string,
): Promise<VenueMedia[]> {
  return http.get<VenueMedia[]>(`/api/v1/admin/venues/${venueId}/media`);
}

export async function addVenueMedia(
  venueId: string,
  data: { url: string; media_type: string; sort_order: number },
): Promise<VenueMedia> {
  return http.post<VenueMedia>(
    `/api/v1/admin/venues/${venueId}/media`,
    data as Record<string, unknown>,
  );
}

export async function deleteVenueMedia(
  venueId: string,
  mediaId: string,
): Promise<void> {
  return http.del(`/api/v1/admin/venues/${venueId}/media/${mediaId}`);
}

// ─── Facilities ──────────────────────────────────────────────────────────────
export async function listVenueFacilities(
  venueId: string,
): Promise<VenueFacility[]> {
  return http.get<VenueFacility[]>(
    `/api/v1/admin/venues/${venueId}/facilities`,
  );
}

export async function addVenueFacility(
  venueId: string,
  data: Partial<VenueFacility>,
): Promise<VenueFacility> {
  return http.post<VenueFacility>(
    `/api/v1/admin/venues/${venueId}/facilities`,
    data as Record<string, unknown>,
  );
}

export async function deleteVenueFacility(
  venueId: string,
  facilityId: string,
): Promise<void> {
  return http.del(
    `/api/v1/admin/venues/${venueId}/facilities/${facilityId}`,
  );
}
