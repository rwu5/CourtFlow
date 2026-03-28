import { http } from "./client";
import type { PaginatedReservations, Reservation } from "@/types";

export async function listReservations(params?: {
  venue_id?: string;
  court_id?: string;
  date_from?: string;
  date_to?: string;
  status?: string;
  page?: number;
  page_size?: number;
}): Promise<PaginatedReservations> {
  const p: Record<string, string | number> = {};
  if (params?.venue_id) p["venue_id"] = params.venue_id;
  if (params?.court_id) p["court_id"] = params.court_id;
  if (params?.date_from) p["date_from"] = params.date_from;
  if (params?.date_to) p["date_to"] = params.date_to;
  if (params?.status) p["status"] = params.status;
  if (params?.page) p["page"] = params.page;
  if (params?.page_size) p["page_size"] = params.page_size;
  return http.get<PaginatedReservations>("/api/v1/admin/reservations", p);
}

export async function getReservation(id: string): Promise<Reservation> {
  return http.get<Reservation>(`/api/v1/admin/reservations/${id}`);
}

export async function cancelReservation(id: string, reason?: string): Promise<Reservation> {
  return http.post<Reservation>(`/api/v1/admin/reservations/${id}/cancel`, reason ? { reason } : {});
}

export async function checkInReservation(id: string): Promise<Reservation> {
  return http.post<Reservation>(`/api/v1/admin/reservations/${id}/check-in`);
}

export async function noShowReservation(id: string): Promise<Reservation> {
  return http.post<Reservation>(`/api/v1/admin/reservations/${id}/no-show`);
}

export async function completeReservation(id: string): Promise<Reservation> {
  return http.post<Reservation>(`/api/v1/admin/reservations/${id}/complete`);
}
