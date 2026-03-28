// ─── Auth ────────────────────────────────────────────────────────────────────
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_id: string;
  is_new_user: boolean;
}

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

export type PlayerLevel = "beginner" | "elementary" | "intermediate" | "advanced" | "professional";
export type DominantHand = "left" | "right";
export type BackhandType = "two_handed" | "one_handed";

// ─── Organization ────────────────────────────────────────────────────────────
export type OrgMemberRole = "owner" | "admin" | "staff" | "coach" | "member";

export interface Organization {
  id: string;
  name: string;
  slug: string;
  logo_url: string | null;
  description: string | null;
  is_active: boolean;
  is_partner: boolean;
  created_at: string;
  updated_at: string;
}

export interface OrganizationMember {
  id: string;
  organization_id?: string;
  user_id: string;
  role: OrgMemberRole;
  is_active: boolean;
  joined_at: string;
  nickname?: string | null;
  phone?: string | null;
  avatar_url?: string | null;
}

// ─── Venue ───────────────────────────────────────────────────────────────────
export interface Venue {
  id: string;
  organization_id: string;
  name: string;
  short_name: string | null;
  address: string;
  city: string;
  district: string | null;
  latitude: number | null;
  longitude: number | null;
  timezone: string;
  phone: string | null;
  wechat_cs: string | null;
  parking_info: string | null;
  open_time: string;
  close_time: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  photos?: string[];
  facilities?: VenueFacility[];
  court_types?: CourtType[];
  courts?: Court[];
}

export interface VenueMedia {
  id: string;
  venue_id: string;
  url: string;
  media_type: "photo" | "banner" | "thumbnail";
  sort_order: number;
}

export interface VenueFacility {
  id: string;
  venue_id: string;
  key: string;
  label: string;
  icon: string | null;
  description: string | null;
}

// ─── Court ───────────────────────────────────────────────────────────────────
export type CourtSurface = "hard" | "clay" | "grass" | "synthetic";

export interface CourtType {
  id: string;
  venue_id: string;
  name: string;
  description: string | null;
  icon: string | null;
  sort_order: number;
}

export interface Court {
  id: string;
  venue_id: string;
  court_type_id: string | null;
  name: string;
  surface: CourtSurface | null;
  is_indoor: boolean;
  slot_duration_minutes: number;
  sort_order: number;
  is_active: boolean;
  created_at: string;
}

export interface CourtMedia {
  id: string;
  court_id: string;
  url: string;
  media_type: "photo" | "banner" | "thumbnail";
  sort_order: number;
}

// ─── Pricing ─────────────────────────────────────────────────────────────────
export interface PricingRule {
  id: string;
  venue_id: string;
  court_id: string | null;
  court_type_id: string | null;
  membership_tier_id: string | null;
  name: string;
  priority: number;
  weekdays: string | null;
  date_from: string | null;
  date_to: string | null;
  time_from: string | null;
  time_to: string | null;
  is_holiday: boolean | null;
  amount_cents: number;
  original_amount_cents: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ─── Membership ──────────────────────────────────────────────────────────────
export type MembershipTierScope = "organization" | "venue" | "court_type" | "court";

export interface MembershipTier {
  id: string;
  organization_id: string;
  scope: MembershipTierScope;
  venue_id: string | null;
  court_type_id: string | null;
  court_id: string | null;
  name: string;
  description: string | null;
  priority: number;
  price_cents: number;
  duration_days: number;
  price_discount_pct: number;
  booking_window_days: number;
  monthly_hour_quota: number | null;
  max_concurrent_bookings: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ─── Reservation ────────────────────────────────────────────────────────────
export type ReservationStatus =
  | "held" | "pending_payment" | "payment_failed"
  | "confirmed" | "checked_in" | "completed"
  | "cancelled" | "admin_cancelled" | "no_show"
  | "refunded" | "partially_refunded";

export interface Reservation {
  id: string;
  user_id: string;
  court_id: string;
  order_id: string | null;
  slot_start_at: string;
  slot_end_at: string;
  status: ReservationStatus;
  amount_cents: number;
  contact_phone: string | null;
  note: string | null;
  checked_in_at: string | null;
  cancelled_at: string | null;
  cancel_reason: string | null;
  created_at: string;
  updated_at: string;
  user_nickname: string | null;
  user_phone: string | null;
  court_name: string;
  venue_name: string;
  venue_id: string;
}

export interface PaginatedReservations {
  items: Reservation[];
  total: number;
  page: number;
  page_size: number;
}

// ─── Court Block ────────────────────────────────────────────────────────────
export interface CourtBlock {
  id: string;
  court_id: string;
  start_at: string;
  end_at: string;
  reason: string | null;
  created_by: string | null;
  created_at: string;
}

// ─── Dashboard Stats ─────────────────────────────────────────────────────────
export interface DashboardStats {
  total_venues: number;
  total_courts: number;
  total_members: number;
  active_pricing_rules: number;
  active_tiers: number;
}
