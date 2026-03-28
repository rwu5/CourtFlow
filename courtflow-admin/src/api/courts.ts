import { http } from "./client";
import type { Court, CourtType, CourtMedia } from "../types";

// ─── Courts ──────────────────────────────────────────────────────────────────
export async function listCourts(venueId: string): Promise<Court[]> {
  return http.get<Court[]>(`/api/v1/admin/venues/${venueId}/courts`);
}

export async function getCourt(
  venueId: string,
  courtId: string,
): Promise<Court> {
  return http.get<Court>(`/api/v1/admin/venues/${venueId}/courts/${courtId}`);
}

export async function createCourt(
  venueId: string,
  data: Partial<Court>,
): Promise<Court> {
  return http.post<Court>(
    `/api/v1/admin/venues/${venueId}/courts`,
    data as Record<string, unknown>,
  );
}

export async function updateCourt(
  venueId: string,
  courtId: string,
  data: Partial<Court>,
): Promise<Court> {
  return http.put<Court>(
    `/api/v1/admin/venues/${venueId}/courts/${courtId}`,
    data as Record<string, unknown>,
  );
}

export async function deleteCourt(
  venueId: string,
  courtId: string,
): Promise<void> {
  return http.del(`/api/v1/admin/venues/${venueId}/courts/${courtId}`);
}

// ─── Court Media ────────────────────────────────────────────────────────────
export async function listCourtMedia(
  venueId: string,
  courtId: string,
): Promise<CourtMedia[]> {
  return http.get<CourtMedia[]>(
    `/api/v1/admin/venues/${venueId}/courts/${courtId}/media`,
  );
}

export async function addCourtMedia(
  venueId: string,
  courtId: string,
  data: { url: string; media_type: string; sort_order: number },
): Promise<CourtMedia> {
  return http.post<CourtMedia>(
    `/api/v1/admin/venues/${venueId}/courts/${courtId}/media`,
    data as Record<string, unknown>,
  );
}

export async function deleteCourtMedia(
  venueId: string,
  courtId: string,
  mediaId: string,
): Promise<void> {
  return http.del(
    `/api/v1/admin/venues/${venueId}/courts/${courtId}/media/${mediaId}`,
  );
}

// ─── Court Types ─────────────────────────────────────────────────────────────
export async function listCourtTypes(
  venueId: string,
): Promise<CourtType[]> {
  return http.get<CourtType[]>(`/api/v1/admin/venues/${venueId}/court-types`);
}

export async function createCourtType(
  venueId: string,
  data: Partial<CourtType>,
): Promise<CourtType> {
  return http.post<CourtType>(
    `/api/v1/admin/venues/${venueId}/court-types`,
    data as Record<string, unknown>,
  );
}

export async function updateCourtType(
  venueId: string,
  typeId: string,
  data: Partial<CourtType>,
): Promise<CourtType> {
  return http.put<CourtType>(
    `/api/v1/admin/venues/${venueId}/court-types/${typeId}`,
    data as Record<string, unknown>,
  );
}

export async function deleteCourtType(
  venueId: string,
  typeId: string,
): Promise<void> {
  return http.del(`/api/v1/admin/venues/${venueId}/court-types/${typeId}`);
}
