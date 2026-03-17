import { http } from "./client";
import type { HoldSlotItem, HoldSlotOut, Order, OrderItem } from "../types";

export async function holdSlots(params: {
  venue_id: string;
  slots: HoldSlotItem[];
  contact_phone?: string;
}): Promise<{ holds: HoldSlotOut[] }> {
  return http.post("/api/v1/bookings/hold", params as Record<string, unknown>);
}

export async function releaseHold(reservationId: string): Promise<void> {
  return http.del(`/api/v1/bookings/hold/${reservationId}`);
}

export async function createOrder(params: {
  reservation_ids: string[];
  contact_phone?: string;
}): Promise<Order> {
  return http.post("/api/v1/orders", params as Record<string, unknown>);
}

export async function listOrders(): Promise<Order[]> {
  return http.get("/api/v1/orders");
}

export async function getOrder(id: string): Promise<Order> {
  return http.get(`/api/v1/orders/${id}`);
}

export async function cancelOrder(id: string): Promise<void> {
  return http.post(`/api/v1/orders/${id}/cancel`);
}
