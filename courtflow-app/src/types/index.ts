// ─── Domain types matching backend API ──────────────────────────────────────

export interface User {
  id: string;
  nickname: string | null;
  phone: string | null;
  avatar_url: string | null;
  bio: string | null;
  gender: string | null;
  player_level: PlayerLevel;
  dominant_hand: DominantHand | null;
  backhand_type: BackhandType | null;
}

export type PlayerLevel =
  | "beginner"
  | "elementary"
  | "intermediate"
  | "advanced"
  | "professional";
export type DominantHand = "left" | "right";
export type BackhandType = "two_handed" | "one_handed";

export interface VenueListItem {
  id: string;
  name: string;
  address: string;
  city: string;
  latitude: number | null;
  longitude: number | null;
  open_time: string;
  close_time: string;
  thumbnail_url: string | null;
  is_partner: boolean;
}

export interface VenueDetail {
  id: string;
  name: string;
  address: string;
  city: string;
  district: string | null;
  latitude: number | null;
  longitude: number | null;
  phone: string | null;
  wechat_cs: string | null;
  parking_info: string | null;
  open_time: string;
  close_time: string;
  slot_duration_minutes: number;
  is_partner: boolean;
  photos: string[];
  facilities: VenueFacility[];
  court_types: CourtType[];
}

export interface VenueFacility {
  key: string;
  label: string;
  icon: string | null;
  description: string | null;
}

export interface CourtType {
  id: string;
  name: string;
  description: string | null;
}

// Slot status as rendered in the booking grid
export type SlotStatus =
  | "available"
  | "unavailable"
  | "booked"
  | "locked"
  | "selected" // client-side selection (not yet held)
  | "held_by_me" // I have an active hold
  | "my_booking"; // I have a confirmed reservation

export interface SlotInfo {
  court_id: string;
  slot_start: string; // ISO8601 UTC
  slot_end: string;
  status: SlotStatus;
  amount_cents: number | null;
  original_amount_cents: number | null;
}

// {court_id: {slot_start_iso: SlotInfo}}
export type AvailabilityGrid = Record<string, Record<string, SlotInfo>>;

export interface HoldSlotItem {
  court_id: string;
  slot_start: string;
  slot_end: string;
}

export interface HoldSlotOut {
  reservation_id: string;
  court_id: string;
  slot_start: string;
  slot_end: string;
  amount_cents: number;
  hold_expires_at: string;
}

export interface OrderItem {
  item_type: string;
  description: string;
  quantity: number;
  unit_price_cents: number;
  total_cents: number;
}

export interface Order {
  id: string;
  status: OrderStatus;
  subtotal_cents: number;
  discount_cents: number;
  total_cents: number;
  contact_phone: string | null;
  items: OrderItem[];
  created_at: string;
}

export type OrderStatus =
  | "pending"
  | "paid"
  | "partially_refunded"
  | "refunded"
  | "cancelled";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_id: string;
  is_new_user: boolean;
}
