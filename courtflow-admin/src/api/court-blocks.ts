import { http } from "./client";
import type { CourtBlock } from "@/types";

export async function listCourtBlocks(venueId: string, courtId: string): Promise<CourtBlock[]> {
  return http.get<CourtBlock[]>(`/api/v1/admin/venues/${venueId}/courts/${courtId}/blocks`);
}

export async function createCourtBlock(
  venueId: string,
  courtId: string,
  data: { start_at: string; end_at: string; reason?: string },
): Promise<CourtBlock> {
  return http.post<CourtBlock>(
    `/api/v1/admin/venues/${venueId}/courts/${courtId}/blocks`,
    data as Record<string, unknown>,
  );
}

export async function deleteCourtBlock(
  venueId: string,
  courtId: string,
  blockId: string,
): Promise<void> {
  return http.del(`/api/v1/admin/venues/${venueId}/courts/${courtId}/blocks/${blockId}`);
}
