# CourtFlow Uni-App Product Plan

**Date:** 2026-03-17
**Status:** Working draft — revised after full screenshot and competitor analysis
**Scope:** Consumer booking app, venue/operator tools, platform architecture, and phased delivery plan

---

## 1. Product Direction

CourtFlow is a **multi-tenant tennis venue commerce platform** — not only a court reservation tool.

The product combines:

- venue discovery (self-operated + partner)
- court slot booking with real-time availability
- order submission and payment (WeChat Pay primary)
- coupons, stored value (wallet), energy points (gamification)
- training/course and coaching entry points
- merchandise/equipment entry points
- user profile with player attributes
- operator tools for pricing, scheduling, and member management

### 1.1 Competitive landscape

| Product | Model | Differentiators |
|---------|-------|-----------------|
| CourtReserve | SaaS for clubs | Reservations, lessons, events, memberships, POS, public booking (Feb 2026) |
| Playtomic | Marketplace | Venues, bookings, open matches, recurring series, club ops |
| Insight Tennis (瑛赛) | Mini-program | Self-operated + partner venues, AI coach, energy points, course upsell |
| Shining Tennis (动之光) | Mini-program | Multi-venue, 30-min slots, linked-court locking, court-type diversity |
| 海南万宁动之光 | Mini-program | 6-court venues, flat pricing, status legend with 5 states |

Sources:
- https://courtreserve.com/features/
- https://courtreserve.com/announcing-public-booking/
- https://third-party.playtomic.io/
- Local reference screenshots (17 images in `courtflow-api/` and `courtflow-api/UI/`)

---

## 2. What The Reference Screenshots Tell Us

### 2.1 Screens captured (17 total)

| # | Screen | Key observations |
|---|--------|-----------------|
| IMG_2968 | **Home page** (Insight Tennis) | Hero banner, energy points (500), training record count, 4 quick-action icons (PK明星, AI教练, 课程, 装备), 4 card entries (self-operated venues, partner venues, group training, sales), bottom tab bar (主页/训练/我的) |
| IMG_2988 | **Home page** (same, UI/ folder) | Identical layout — confirms stable design |
| IMG_2970 | **Venue detail** | Photo gallery, venue name, hours (7:00–22:00), address, 4 action buttons (电话咨询/客服微信/地图导航/停车指引), facility tags with icons (高楼层球场/加宽学练场/基础学练场/中面训练场) |
| IMG_2988 | **Self-operated venue list** | Card layout with photo, name, address, distance, favorite button, "预订" CTA |
| IMG_2989 | **Partner venue list** | Same card layout, cross-link to self-operated list |
| IMG_2969 | **Booking grid** (Insight Tennis) | Date tabs (03-14 to 03-18+), 3 courts (场地01/02/03), 1-hour slots, prices (¥98–¥148), strikethrough original prices, greyed unavailable slots |
| IMG_2984 | **Booking grid** (same venue, different day) | 3 courts, prices ¥68–¥108, strikethrough prices visible |
| IMG_2986 | **Booking grid with selections** | Multiple slots selected (highlighted green), multi-court multi-time selection, running total ¥404 |
| IMG_2965 | **Booking grid** (competitor, purple) | 30-min slots, 4+ court types (练习馆教练课/网球标准场教.../1球道(8米宽)/3球道), all slots "不可预订" (unavailable) at night |
| IMG_2966 | **Booking grid** (competitor, daytime) | Prices ¥100–¥150, "关联锁场" (linked-court lock) status on some courts |
| IMG_2967 | **Booking grid** (competitor, another venue) | 4 courts, prices ¥49–¥150, mixed availability |
| IMG_2971 | **Booking grid** (teal theme) | 6 courts, ¥35–¥100 flat pricing, 5-state legend (可选/已定/已选/待支付/我的预约) |
| IMG_2985 | **Order submit** (single slot) | Venue photo+name+address, date/court/time, refund policy link, phone, coupon entry, energy points (toggle with +/- stepper), stored-value toggle, total ¥128 |
| IMG_2987 | **Order submit** (multi-slot) | 3 slots across different courts and times, same payment options, total ¥404 |
| IMG_2983 | **Profile edit** | Avatar, nickname, phone (editable), gender (先生/女士), birthday, email, self-rated level (新手), dominant hand (左手/右手), backhand type (双手反手/单手反手) |
| IMG_2991 | **WeChat phone auth** | Shining Tennis branded, phone number verification dialog |
| IMG_2992 | **New user onboarding** | Avatar upload, nickname, signature/bio input |

### 2.2 Design patterns extracted

**Booking grid (the product core):**
- Horizontal: courts as columns, scrollable when >3
- Vertical: time slots as rows (30-min or 1-hour configurable per venue)
- Date selector: horizontal scrolling day tabs with day-of-week labels
- Cell states: available (white/priced), selected (green highlight), unavailable (grey), locked (关联锁场), pending-payment, my-booking
- Price display: current price prominent, original/strikethrough price below
- Footer: running total + "场地预订" submit button

**Venue detail:**
- Photo gallery (swipeable)
- Venue name + hours
- Full address
- 4 action buttons in 2x2 grid: phone, WeChat CS, map nav, parking
- Facility type tags with icons
- Full-width "场地预订" CTA at bottom

**Order submit:**
- Venue card (photo + name + address)
- Slot list (date + court + time per line)
- Refund policy link
- Phone number (pre-filled, editable)
- Coupon/pass card selector
- Energy points stepper (current balance shown, +/- buttons)
- Stored-value toggle (balance shown)
- Price breakdown + total
- "立即支付" submit button

**Home page:**
- User greeting with avatar + energy points + training record count
- Hero banner/carousel
- 4 quick-action icon row (PK stars, AI coach, courses, equipment)
- 4 feature cards in 2x2 grid (self-operated venues, partner venues, group training, sales/promotions)
- 3-tab bottom nav: 主页 / 训练 / 我的

### 2.3 Implications for CourtFlow

1. **Court types are a first-class concept** — not just numbered courts, but typed facilities (standard court, training lane, coaching room) with different pricing and availability patterns.

2. **Slot granularity must be configurable** — 30-min and 1-hour slots both exist in the market. This should be a venue-level setting.

3. **5-state slot model in the grid** — our booking state machine needs to map cleanly to grid cell rendering: available, booked-by-others, selected-by-me, pending-my-payment, my-confirmed-booking.

4. **Energy points are a gamification layer** — separate from wallet/stored-value. Earned through activities, spent as payment discount. This is a Phase 2 feature but the data model should accommodate it.

5. **Linked-court locking (关联锁场)** — some venues pair courts for doubles or events. This requires a court-linking or court-group concept.

6. **3-tab nav is sufficient for MVP** — 主页/训练/我的. The 5-tab structure proposed in v1 is over-scoped for launch.

---

## 3. Recommended Architecture

### 3.1 Frontend surfaces

| Surface | Tech | Target | Priority |
|---------|------|--------|----------|
| **Player app** | uni-app + Vue 3 + TypeScript | WeChat Mini Program (primary), H5 (secondary) | Phase 1 |
| **Venue operator console** | Vue 3 + Vite + Element Plus | Desktop web | Phase 1 (lite) |
| **Platform admin** | Same stack or separate routes | Desktop web | Phase 2 |

### 3.2 Backend

- **API:** FastAPI (Python 3.12+)
- **DB:** PostgreSQL 16 with SQLAlchemy 2.0 + Alembic
- **Cache/Jobs:** Redis 7 + ARQ (async task queue)
- **Storage:** S3-compatible (Cloudflare R2 or AWS S3)
- **Payments:** WeChat Pay (primary), Alipay (secondary), provider adapter layer
- **Notifications:** WeChat subscription messages first, SMS second

### 3.3 Multi-tenant hierarchy

```
Platform (CourtFlow)
  └─ Organization (brand/chain, e.g. "瑛赛网球")
       └─ Venue (physical location, e.g. "陆家嘴尚悦湾店")
            └─ Court (bookable resource, e.g. "场地01 — 基础学练场")
```

Key: `organization ≠ venue`. One org can have many venues. This is confirmed by the screenshots showing multi-location brands.

---

## 4. Core Product Modules

### 4.1 Consumer modules

#### M1: Authentication and identity
- WeChat login (wx.login → code → server exchange)
- Phone number authorization (WeChat getPhoneNumber button)
- New user onboarding (avatar, nickname, signature)
- Profile editing: gender, birthday, email, self-rated level (新手/初级/中级/高级/专业), dominant hand, backhand type
- Session management with refresh tokens

#### M2: Home and discovery
- User greeting bar (avatar, energy points, training record count)
- Hero banner/carousel (admin-configurable)
- Quick-action icon row (configurable, initially: PK stars, AI coach, courses, equipment)
- Feature card grid: self-operated venues, partner venues, group training, promotions
- Bottom tab navigation: 主页 / 训练 / 我的

#### M3: Venue discovery
- Self-operated venue list (card layout: photo, name, address, distance, favorite, book CTA)
- Partner venue list (same layout, cross-link)
- Filters: distance, district, indoor/outdoor, surface type, price range, availability
- Venue detail page:
  - Photo gallery (swipeable)
  - Name + operating hours
  - Address (tappable for map)
  - Action buttons: phone, WeChat CS, map navigation, parking guide
  - Facility type tags with icons
  - Full-width "场地预订" CTA

#### M4: Availability and booking
- Date selector (horizontal day tabs, day-of-week labels)
- Booking grid:
  - Courts as columns (horizontally scrollable)
  - Time slots as rows (granularity configurable: 30min or 60min per venue)
  - Cell states: available (white + price), selected (green), unavailable (grey), locked (关联锁场), pending-payment (yellow), my-booking (blue)
  - Price display: current price + strikethrough original
  - Multi-slot selection across courts and times
  - Running total in footer
- "场地预订" button → order submit page
- Hold-before-pay (5-minute TTL)
- Booking confirmation push notification

#### M5: Order and payment
- Order submit page:
  - Venue card (photo + name + address)
  - Selected slot list (date + court + time per row)
  - Refund policy link
  - Pre-filled phone (editable)
  - Coupon/pass card selector ("您有可用优惠券 >>")
  - Energy points: current balance, +/- stepper, deduction amount
  - Stored-value: balance display, toggle on/off, deduction amount
  - Price breakdown: subtotal, coupon discount, points discount, wallet discount, total
  - "立即支付" button → WeChat Pay
- Payment result page (success/fail)
- Order list (upcoming / past / cancelled)
- Order detail with cancellation and refund visibility

#### M6: My account
- Booking history
- Coupons list
- Wallet / stored value
- Energy points history
- Favorites (venues)
- Training records
- Settings
- Support / feedback

### 4.2 Venue operator modules (web console)

#### O1: Venue setup
- Venue profile (name, address, geo, hours, contact, parking info)
- Photo management (gallery, thumbnails)
- Facility types and tags

#### O2: Court management
- Create/edit courts with type labels (标准场, 学练场, 球道, etc.)
- Surface, dimensions, capacity
- Slot granularity setting (30min / 60min)
- Court linking/grouping (for linked-court locking)
- Maintenance blocks and closures

#### O3: Pricing rules
- Rules by: weekday, date range, time band, court, court type, holiday, member tier
- Priority-based evaluation
- Peak/off-peak presets
- Strikethrough (original) price support
- Preview pricing grid before publishing

#### O4: Booking operations
- Reservation list with filters and search
- Check-in (scan or manual)
- No-show handling
- Manual booking (walk-ins, phone)
- Cancel/refund actions
- Conflict inspector

#### O5: Member and CRM
- Member list with tags and tiers
- Coupon issuance
- Stored-value adjustments
- Energy points adjustments
- Package balances

#### O6: Reports
- Revenue (daily/weekly/monthly)
- Court utilization heatmap
- Order breakdown
- Cancellation/refund report
- Coupon redemption report

### 4.3 Platform modules (Phase 2+)

1. Organization onboarding and approval
2. Partner venue approval workflow
3. Settlement and commission management
4. Payment account review
5. Cross-tenant reporting
6. Feature flags by tenant
7. Support tooling and audit logs

---

## 5. Data Model

### 5.1 Core tables (keep from DESIGN.md)

| Table | Notes |
|-------|-------|
| `users` | Global, non-tenant-scoped |
| `organizations` | Brand/chain |
| `organization_members` | User↔org with roles and tiers |
| `membership_tiers` | Per-org benefit levels |
| `courts` | Bookable resources under venues |
| `operating_schedules` | Day-of-week and date-specific hours |
| `court_blocks` | Maintenance windows |
| `pricing_rules` | Time/day/court pricing |
| `discounts` | Coupon definitions |
| `reservations` | Core booking records |
| `payments` | Provider-agnostic payment records |
| `audit_log` | Change trail |

### 5.2 New/modified tables needed

| Table | Purpose | Phase |
|-------|---------|-------|
| `venues` | Physical locations under organizations (address, geo, hours, contact, parking) | 1 |
| `venue_media` | Photos, banners, thumbnails | 1 |
| `venue_facilities` | Facility type tags with icons (高楼层球场, etc.) | 1 |
| `court_types` | Named court categories per venue (标准场, 学练场, 球道) | 1 |
| `court_links` | Linked/paired courts for group locking (关联锁场) | 2 |
| `orders` | Parent commerce entity spanning reservations, courses, merchandise | 1 |
| `order_items` | Individual line items within an order | 1 |
| `wallet_accounts` | Stored-value balance per user per org | 2 |
| `wallet_transactions` | Recharge, deduction, refund, adjustment | 2 |
| `energy_accounts` | Gamification points balance per user | 2 |
| `energy_transactions` | Earn, spend, expire, adjust | 2 |
| `coupon_instances` | User-owned coupon records (claimed from discount definitions) | 2 |
| `packages` | Prepaid time/lesson/session packs | 2 |
| `package_usages` | Balance-consuming actions | 2 |
| `courses` | Course catalog | 3 |
| `course_sessions` | Scheduled instances | 3 |
| `coach_profiles` | Bio, specialization, venue assignment | 3 |
| `products` | Merchandise catalog | 3 |
| `check_ins` | Venue arrival tracking | 2 |
| `banners` | Home page carousel content | 1 |
| `quick_actions` | Home page icon row config | 1 |

### 5.3 Reservation state machine

```
held (5min TTL)
  → expired (auto)
  → pending_payment (user submits order)
      → confirmed (payment success)
          → checked_in (venue scan/manual)
              → completed (auto after end time)
          → completed (auto after end time, no check-in)
          → cancelled (user cancel within policy)
          → admin_cancelled (operator cancel)
      → payment_failed (payment error)
          → held (retry)
          → expired (timeout)
  → cancelled (user abandons)

confirmed → no_show (auto 30min after start, no check-in)
cancelled/admin_cancelled → refunded / partially_refunded
```

### 5.4 Grid cell state mapping

| Cell state | Visual | Source |
|------------|--------|--------|
| `available` | White, price shown | No reservation for this slot |
| `unavailable` | Grey, "不可预订" | Past time, court block, or operating hours |
| `booked` | Grey, no price | Reservation by another user (confirmed/checked_in) |
| `selected` | Green highlight | Current user's selection (client-side, pre-hold) |
| `held_by_me` | Yellow/amber | Current user has a hold (pending payment) |
| `my_booking` | Blue/teal | Current user's confirmed reservation |
| `locked` | Grey, "关联锁场" | Court linked to another court's booking |

---

## 6. Booking Engine Requirements

Non-negotiable capabilities:

1. **Prevent double booking** — three-layer: DB unique constraint + Redis atomic check + application-level validation
2. **Hold-and-release** — 5-minute TTL, Redis-backed, auto-expire via background job
3. **Accurate availability grid** — per-court per-slot status, cached in Redis (30s TTL), invalidated on booking state change
4. **Dynamic pricing** — compute price per slot based on rules (time, day, date, court type, member tier, holiday)
5. **Multi-slot one-order checkout** — aggregate slots from different courts/times into single order
6. **Payment orchestration** — support coupon + energy points + wallet + WeChat Pay in single transaction
7. **Operator overrides** — manual booking, cancel, refund, court block
8. **Linked-court locking** — when court A is booked, linked court B auto-locks for that slot
9. **Configurable slot granularity** — 30min or 60min per venue
10. **Audit trail** — every booking state change logged

---

## 7. Technical Decisions for Uni-App

### 7.1 Frontend stack

- `uni-app` with Vue 3 Composition API
- TypeScript (strict mode)
- Pinia for state management
- `uni-ui` for basic components, custom domain components for booking grid
- Typed API client layer (auto-generated from OpenAPI spec)
- Subpackages for code splitting and performance

### 7.2 Project structure

```
courtflow-app/
├── src/
│   ├── pages/                    # Main package pages
│   │   ├── index/                # Home
│   │   ├── login/                # Auth
│   │   └── webview/              # External content
│   ├── packages/
│   │   ├── venue/                # Venue list, detail
│   │   ├── booking/              # Grid, order submit, payment result
│   │   ├── account/              # Profile, orders, coupons, wallet
│   │   └── training/             # Courses, coaches (Phase 3)
│   ├── components/
│   │   ├── ui/                   # Generic UI components
│   │   └── domain/
│   │       ├── BookingGrid/      # The core matrix component
│   │       ├── SlotCell/         # Individual grid cell
│   │       ├── VenueCard/        # Venue list card
│   │       ├── OrderSlotList/    # Slot summary in checkout
│   │       └── PriceBreakdown/   # Payment detail breakdown
│   ├── stores/
│   │   ├── auth.ts
│   │   ├── booking.ts
│   │   ├── venue.ts
│   │   └── user.ts
│   ├── api/
│   │   ├── client.ts             # Base HTTP client with interceptors
│   │   ├── auth.ts
│   │   ├── venues.ts
│   │   ├── booking.ts
│   │   ├── orders.ts
│   │   └── user.ts
│   ├── utils/
│   ├── types/
│   └── static/
├── pages.json
├── manifest.json
├── uni.scss
└── tsconfig.json
```

### 7.3 Critical client-side challenges

1. **Booking grid rendering performance**
   - The matrix is the product core — it must be buttery smooth
   - Virtualize rows for venues with many time slots
   - Horizontal scroll for >3 courts with sticky time column
   - Debounce slot selection to avoid jank

2. **Optimistic selection vs server authority**
   - Client-side: instant green highlight on tap
   - Server: hold request fires immediately, UI reverts if hold fails (slot taken)
   - Show "抢占中..." loading state on cell during hold request

3. **WeChat-specific flows**
   - `wx.login()` → code → server → session
   - `getPhoneNumber` button component → encrypted phone → server decrypt
   - `wx.requestPayment()` → unified order → payment
   - `wx.openLocation()` → map navigation
   - `wx.makePhoneCall()` → venue phone
   - `subscribeMessage` → booking confirmation push

4. **Multi-slot state management**
   - Pinia store tracks selected slots as `Map<slotId, SlotInfo>`
   - Running total computed reactively
   - Cross-court selection supported
   - Clear all on navigation away or timeout

---

## 8. API Contract Overview

### 8.1 Player app APIs

```
POST   /api/v1/auth/wechat-login          # code → session token
POST   /api/v1/auth/bind-phone             # encrypted phone → bind
GET    /api/v1/auth/me                     # current user profile
PUT    /api/v1/auth/me                     # update profile

GET    /api/v1/venues                      # list (with geo, filters)
GET    /api/v1/venues/:id                  # detail
GET    /api/v1/venues/:id/availability     # grid data for date range
POST   /api/v1/venues/:id/favorites        # toggle favorite

POST   /api/v1/bookings/hold               # hold selected slots (5min)
DELETE /api/v1/bookings/hold/:holdId        # release hold
POST   /api/v1/orders                      # submit order (slots + payment method)
GET    /api/v1/orders                      # my orders list
GET    /api/v1/orders/:id                  # order detail
POST   /api/v1/orders/:id/cancel           # cancel order

POST   /api/v1/payments/wechat/create      # create WeChat unified order
POST   /api/v1/payments/wechat/callback    # WeChat payment notification (server-to-server)

GET    /api/v1/coupons                     # my coupons
GET    /api/v1/wallet                      # my wallet balance
GET    /api/v1/energy                      # my energy points

GET    /api/v1/banners                     # home page banners
```

### 8.2 Operator APIs

```
GET/PUT   /api/admin/venues/:id                    # venue settings
CRUD      /api/admin/venues/:id/courts             # court management
CRUD      /api/admin/venues/:id/court-types        # court type definitions
CRUD      /api/admin/venues/:id/pricing-rules      # pricing rules
CRUD      /api/admin/venues/:id/court-blocks       # maintenance blocks
GET       /api/admin/venues/:id/reservations       # reservation list
POST      /api/admin/venues/:id/reservations       # manual booking
PUT       /api/admin/venues/:id/reservations/:id   # update (check-in, cancel, no-show)
POST      /api/admin/venues/:id/reservations/:id/refund
GET       /api/admin/venues/:id/members            # member list
GET       /api/admin/venues/:id/reports/*           # various reports
CRUD      /api/admin/venues/:id/coupons            # coupon management
```

---

## 9. Information Architecture

### 9.1 Consumer app — 3-tab bottom navigation

| Tab | Icon | Primary page | Sub-pages |
|-----|------|-------------|-----------|
| **主页** (Home) | 🏠 | Home feed | — |
| **训练** (Training) | 🎾 | Training hub | Courses, coaches, AI coach (Phase 3) |
| **我的** (My) | 👤 | My account | Profile, orders, coupons, wallet, energy, favorites, settings |

### 9.2 Consumer page map

```
Home (tabbar)
├── Self-operated venue list
│   └── Venue detail
│       └── Booking grid
│           └── Order submit
│               └── Payment result
├── Partner venue list
│   └── Venue detail → (same flow)
├── Group training list (Phase 3)
├── Promotions / sales (Phase 2)

Training (tabbar)
├── Course list (Phase 3)
├── Coach list (Phase 3)
├── AI coach entry (Phase 3+)
├── Training records

My (tabbar)
├── Profile edit
├── My orders
│   └── Order detail
│       └── Cancel / refund
├── My coupons
├── My wallet
├── Energy points
├── Favorites
├── Settings
└── Support / feedback
```

### 9.3 Operator console page map

```
Dashboard (utilization, revenue, today's bookings)
├── Venue settings
├── Courts
│   ├── Court list
│   ├── Court types
│   └── Court links
├── Schedule
│   ├── Operating hours
│   ├── Court blocks / closures
│   └── Pricing rules
│       └── Price preview grid
├── Reservations
│   ├── Reservation list (with filters)
│   ├── Check-in view
│   └── Manual booking
├── Members
│   ├── Member list
│   ├── Coupon issuance
│   └── Wallet / points adjustment
├── Reports
│   ├── Revenue
│   ├── Utilization heatmap
│   ├── Orders
│   └── Cancellations
└── Settings
```

---

## 10. MVP Scope

### 10.1 MVP in (Phase 1)

**Consumer app:**
- WeChat login + phone bind + onboarding
- Home page (banner, quick actions, venue entry cards)
- Self-operated venue list + venue detail
- Booking grid (1-hour slots, up to ~6 courts)
- Multi-slot selection + running total
- Hold-before-pay (5min)
- Order submit with price breakdown
- WeChat Pay
- Order list + order detail + cancellation
- Basic profile editing (name, phone, gender, level, hand, backhand)
- My account tab

**Operator console (lite):**
- Venue profile editing
- Court CRUD with types
- Operating hours
- Pricing rules (weekday/time band/court)
- Reservation list + manual booking
- Cancel/refund actions

**Backend:**
- Auth (WeChat + phone)
- Venue, court, schedule, pricing CRUD
- Availability grid computation + Redis cache
- Hold engine
- Order + payment (WeChat Pay)
- Reservation state machine
- Basic audit log

### 10.2 MVP out

- Partner venues (discovery only, no onboarding flow)
- Coupons, wallet, energy points (deduction UI shown but disabled)
- Linked-court locking
- Recurring bookings
- Training / courses / coaches
- Merchandise
- Memberships / packages
- Check-in
- Notifications (beyond payment confirmation)
- AI coach
- Open matches / social play
- Multi-provider payments (Alipay, card)

### 10.3 MVP success criteria

1. A user can discover a venue, view availability, select slots, pay, and see their booking
2. An operator can set up courts and pricing, view reservations, and process cancellations
3. The system prevents double-booking under concurrent load
4. The booking grid renders smoothly with 6 courts × 16 hours of slots

---

## 11. Phased Delivery Plan

### Phase 0: Foundation (1–2 weeks)

- [ ] Finalize tenant hierarchy and data model
- [ ] Set up uni-app project scaffold with TypeScript + Pinia
- [ ] Set up FastAPI project with PostgreSQL + Redis + Alembic
- [ ] Implement DB migrations for core tables (users, orgs, venues, courts, schedules, pricing_rules, reservations, payments, orders, audit_log)
- [ ] Implement WeChat login + phone bind backend
- [ ] Define OpenAPI spec for Phase 1 endpoints
- [ ] Set up operator console scaffold (Vue 3 + Vite + Element Plus)
- [ ] Design tokens and component library foundation

### Phase 1: Booking MVP (3–4 weeks)

- [ ] Home page (static content, venue entry points)
- [ ] Venue list + venue detail pages
- [ ] Booking grid component (the critical path)
- [ ] Hold engine (Redis-backed, 5min TTL, background expiry)
- [ ] Order submit flow + WeChat Pay integration
- [ ] Payment result + order confirmation
- [ ] Order list + detail + cancellation
- [ ] Profile editing
- [ ] Operator: venue setup, court CRUD, pricing rules, reservation list, manual booking
- [ ] End-to-end testing: book → pay → confirm → cancel → refund

### Phase 2: Monetization and engagement (3–4 weeks)

- [ ] Coupon system (definitions, issuance, claiming, redemption at checkout)
- [ ] Stored-value wallet (recharge, deduction, balance display)
- [ ] Energy points (earn rules, spend at checkout, balance)
- [ ] Memberships and member tiers
- [ ] Packages (prepaid sessions)
- [ ] Check-in (QR scan or manual)
- [ ] Partner venue discovery + onboarding flow
- [ ] Linked-court locking
- [ ] WeChat subscription message notifications
- [ ] Operator: member CRM, coupon issuance, wallet/points adjustment, reports

### Phase 3: Programs and commerce (3–4 weeks)

- [ ] Course catalog and enrollment
- [ ] Coach profiles and scheduling
- [ ] Group training
- [ ] Private lessons
- [ ] Training tab content
- [ ] Merchandise catalog + pickup orders
- [ ] Promotions / sales page
- [ ] Recurring reservations

### Phase 4: Platform scale (ongoing)

- [ ] Multi-org platform admin
- [ ] Commission settlement
- [ ] Cross-venue memberships
- [ ] Public booking links (shareable)
- [ ] Waitlists
- [ ] Advanced analytics and reporting
- [ ] Feature flags per tenant
- [ ] AI coach integration

---

## 12. Analytics Events (Day 1)

Track from launch:

| Event | Trigger |
|-------|---------|
| `app_open` | App launch |
| `login_success` | WeChat login complete |
| `home_view` | Home tab loaded |
| `venue_list_view` | Venue list opened (self/partner) |
| `venue_detail_view` | Venue detail opened |
| `venue_favorite` | Favorite toggled |
| `grid_view` | Booking grid loaded |
| `slot_select` | Slot tapped (with court, time, price) |
| `slot_deselect` | Slot un-tapped |
| `checkout_start` | Order submit page opened |
| `coupon_apply` | Coupon selected (Phase 2) |
| `payment_start` | "立即支付" tapped |
| `payment_success` | WeChat Pay callback success |
| `payment_fail` | Payment failed/cancelled |
| `booking_cancel` | User cancels booking |
| `profile_update` | Profile saved |

---

## 13. Key Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Booking grid performance** | Core UX degraded, users abandon | Virtualize rows, limit initial render to visible viewport, profile on low-end devices |
| **Double booking under load** | Trust destroyed | Three-layer prevention (DB constraint + Redis atomic + app check), load test before launch |
| **WeChat Pay integration complexity** | Launch blocked | Start integration in Phase 0, use sandbox early, have manual payment fallback |
| **Under-modeling venues** | Painful rework when adding partner venues | Build venue layer from day 1, even if only self-operated at launch |
| **Weak operator tooling** | Ops team can't function, escalations flood | Ship operator console in parallel with consumer app, not after |
| **Scope creep into AI/social features** | MVP delayed | Hard Phase 1 cutline — no AI coach, no social play, no merchandise until Phase 3 |
| **Payment orchestration complexity** | Coupon + wallet + points + real payment = many edge cases | Phase 1: WeChat Pay only, no discounts. Phase 2: add one payment method at a time with thorough testing |

---

## 14. Execution Priorities

**Build order:**
1. FastAPI backend (auth + venues + booking engine + payments)
2. uni-app consumer client (home → venue → grid → order → pay → my orders)
3. Vue web operator console (courts + pricing + reservations)
4. Platform admin (Phase 2+)

**Critical path items:**
1. Booking grid component — start prototyping immediately, it's the product
2. WeChat Pay integration — long lead time, start in Phase 0
3. Hold engine — must work correctly before any booking flow exists
4. Availability computation — the query that powers the grid

**What to build first each day:**
- Backend API → Frontend page that consumes it → Operator page that manages it

---

## 15. Recommendation

Build CourtFlow as:

> **A multi-tenant tennis venue commerce platform with WeChat Mini Program-first booking, dynamic pricing, multi-slot checkout, and integrated operator tooling.**

The MVP proves: users can discover → book → pay → manage. Operators can configure → price → manage → report.

Everything else (coupons, wallet, points, courses, merchandise, AI, social) layers on top of this foundation without re-architecture.
