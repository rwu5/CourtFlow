# CourtFlow — RallyAI Tennis Venue Platform

> A multi-tenant tennis venue commerce platform combining court discovery, real-time slot booking, dynamic pricing, membership management, and coaching — built for WeChat Mini Program and H5.

---

## Table of Contents

- [Product Overview](#product-overview)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Backend — courtflow-api](#backend--courtflow-api)
  - [Module Map](#module-map)
  - [Data Model Hierarchy](#data-model-hierarchy)
  - [Reservation Engine](#reservation-engine)
  - [Pricing Engine](#pricing-engine)
  - [Membership System](#membership-system)
  - [API Reference](#api-reference)
- [Frontend — courtflow-app](#frontend--courtflow-app)
  - [Page Structure](#page-structure)
  - [Design System](#design-system)
  - [State Management](#state-management)
- [Getting Started](#getting-started)
- [Roadmap](#roadmap)

---

## Product Overview

CourtFlow targets tennis players and venue operators in China. It is positioned as a full-stack commerce platform — not just a reservation tool.

| Capability | Description |
|---|---|
| **Court discovery** | Browse self-operated and partner venues by location, surface type, and indoor/outdoor |
| **Real-time booking** | Date × court × time-slot grid with live availability, hold-then-pay flow |
| **Dynamic pricing** | Rule-based pricing engine: weekday, time window, holiday, membership tier |
| **Memberships** | Court-specific, venue-wide, or org-wide tiers with pricing benefits and booking priority |
| **Discounts** | Coupon codes, promo codes, auto-applied discounts (flat, percent, free slot) |
| **Coaching** | Coach profiles, availability, lesson booking (Phase 2) |
| **Gamification** | Energy points, training records (Phase 2) |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                        │
│   WeChat Mini Program  ·  H5 (browser)                  │
│         courtflow-app  (uni-app / Vue 3)                 │
└────────────────────────┬────────────────────────────────┘
                         │  HTTPS / REST
┌────────────────────────▼────────────────────────────────┐
│                   API Gateway / LB                       │
│         (rate limiting · SSL termination)               │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              Application Core (FastAPI)                  │
│                  courtflow-api                           │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │ Booking  │  │ Pricing  │  │ Members  │  │  Auth  │  │
│  │ Engine   │  │ Engine   │  │  & Tiers │  │  JWT   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘  │
└───────┼─────────────┼─────────────┼─────────────┼───────┘
        │             │             │             │
┌───────▼─────────────▼─────────────▼─────────────▼───────┐
│                   Infrastructure                         │
│  PostgreSQL 16   ·   Redis 7   ·   S3 (Cloudflare R2)   │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

- **Shared-database multi-tenancy** — `Organization → Venue → Court` hierarchy with `org_id` discriminator columns; no cross-tenant data leakage, no per-tenant DB overhead.
- **3-layer double-booking prevention** — Redis `SETNX` hold → DB uniqueness constraint → async ARQ job to expire stale holds. Prevents race conditions at every layer.
- **Domain-driven modules** — Booking, Pricing, Payment, Identity, and Organization are separated at the code level for independent evolution.
- **Event-driven side effects** — Confirmation emails, payment capture, hold expiry run through ARQ background jobs, keeping the critical request path fast.

---

## Tech Stack

### Backend

| Layer | Technology | Why |
|---|---|---|
| API server | **FastAPI** (Python 3.12+) | Async-native, auto OpenAPI docs, Pydantic v2 validation |
| Database | **PostgreSQL 16** | Row-level locking, JSONB, partial indexes, timezone support |
| ORM | **SQLAlchemy 2.0** + **Alembic** | Async sessions, typed mapped columns, battle-tested migrations |
| Cache / Queue | **Redis 7** + **ARQ** | Slot hold cache (`SETNX`), background job queue (hold expiry) |
| Auth | **JWT** (python-jose) + **passlib** | Multi-role, multi-tenant claims; refresh token rotation |
| Payments | **WeChat Pay** (primary), Alipay adapter | Adapter pattern allows provider swap without core changes |
| Storage | **S3-compatible** (Cloudflare R2 / AWS S3) | Venue photos, coach avatars, banners |
| HTTP client | **httpx** | Async calls to WeChat OAuth and payment APIs |

### Frontend

| Layer | Technology | Why |
|---|---|---|
| Framework | **uni-app** (Vue 3 + TypeScript) | Single codebase targets WeChat Mini Program, H5, and other platforms |
| Build | **Vite** | Fast HMR, tree-shaking, TypeScript-first |
| State | **Pinia** | Vue 3 native, composable stores |
| UI | Custom design system (`uni.scss`) | Glassmorphic dark theme; no external UI lib dependency on Mini Program |

---

## Repository Structure

```
CourtFlow/
├── courtflow-api/          # FastAPI backend
│   ├── app/
│   │   ├── api/v1/
│   │   │   └── endpoints/  # auth · venues · bookings · orders · memberships
│   │   ├── core/           # config · database · security · deps
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── services/       # booking · pricing · availability
│   │   └── tasks/          # ARQ background jobs (hold expiry)
│   ├── alembic/            # DB migrations
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   ├── seeds/              # Dev data seeding
│   ├── tests/
│   ├── DESIGN.md           # Full architecture & design document
│   └── requirements.txt
│
├── courtflow-app/          # uni-app frontend
│   └── src/
│       ├── pages/          # Tab pages (home · courts · courses · my · login)
│       ├── packages/       # Lazy-loaded sub-packages
│       │   ├── venue/      # detail · list · booking
│       │   ├── booking/    # order · result
│       │   ├── account/    # orders · profile
│       │   ├── coach/      # coach profile
│       │   └── membership/ # join flow
│       ├── components/
│       │   ├── ui/         # CfIcon · CfTabBar
│       │   └── domain/     # BookingGrid
│       ├── stores/         # Pinia: auth · booking
│       ├── api/            # API client (auth · venues · bookings)
│       ├── types/          # TypeScript interfaces
│       └── uni.scss        # Design system tokens
│
├── UNI_APP_PRODUCT_PLAN.md # Product requirements & competitive analysis
└── README.md
```

---

## Backend — courtflow-api

### Module Map

```
app/
├── api/v1/endpoints/
│   ├── auth.py          # POST /auth/wechat · POST /auth/refresh · POST /auth/logout
│   ├── venues.py        # GET /venues · GET /venues/{id} · GET /venues/{id}/availability
│   ├── bookings.py      # POST /bookings/hold · POST /bookings/confirm · DELETE /bookings/{id}
│   ├── orders.py        # POST /orders · GET /orders/{id} · POST /orders/{id}/pay
│   ├── memberships.py   # GET /memberships/tiers · POST /memberships/join
│   │                    # GET /memberships/my · POST /memberships/{id}/cancel
│   └── users.py         # GET/PATCH /users/me
│
├── models/
│   ├── organization.py  # Organization · MembershipTier · UserMembership · OrganizationMember
│   ├── venue.py         # Venue · VenueMedia · VenueFacility
│   ├── court.py         # Court · CourtType · CourtBlock · CourtLink
│   ├── reservation.py   # Reservation (hold → confirm → complete)
│   ├── order.py         # Order · OrderItem
│   ├── pricing.py       # PricingRule
│   ├── discount.py      # Discount (coupon/promo/auto)
│   ├── payment.py       # Payment · PaymentAccount
│   ├── schedule.py      # OperatingSchedule (weekday defaults + date overrides)
│   └── user.py          # User · RefreshToken
│
└── services/
    ├── booking.py       # hold_slot() · confirm_slot() · release_hold()
    ├── pricing.py       # resolve_price() — rule evaluation with membership context
    └── availability.py  # get_availability_grid() — Redis-cached slot grid
```

### Data Model Hierarchy

```
Organization
└── Venue  (location, hours, slot_duration_minutes, timezone)
    ├── Court  (surface, is_indoor, sort_order)
    │   ├── CourtBlock   (maintenance windows)
    │   └── CourtLink    (linked-court locking for doubles / training lanes)
    ├── CourtType        (named categories: 标准场, 学练场, 球道8米…)
    ├── OperatingSchedule (weekday defaults + date-specific overrides)
    ├── PricingRule      (time/weekday/holiday/membership conditions → price)
    └── VenueMedia / VenueFacility

MembershipTier  (scoped to org | venue | court_type | court)
└── UserMembership  (user × tier, starts_at / expires_at, status)

Order
├── Reservation  (user × court × slot, hold → confirmed → completed)
├── OrderItem    (line items: reservation | course | product)
└── Payment      (WeChat Pay / Alipay transaction record)
```

### Reservation Engine

The booking flow uses a 3-layer guard against double-booking:

```
1. Redis SETNX  ──▶  key: hold:{court_id}:{date}:{slot_start}
                     TTL: 5 minutes
                     Atomic: prevents concurrent holds

2. DB CHECK     ──▶  SELECT ... WHERE court_id = ? AND slot_date = ?
                     AND slot_start = ? AND status != 'cancelled'
                     Catches any Redis bypass

3. DB UNIQUE    ──▶  UNIQUE CONSTRAINT (court_id, slot_date, slot_start)
                     Hard database-level guarantee

4. ARQ Job      ──▶  expire_holds() runs every 60s
                     Releases Redis key + sets Reservation.status = 'cancelled'
                     for holds past hold_expires_at
```

Reservation states:

```
held ──▶ pending_payment ──▶ confirmed ──▶ checked_in ──▶ completed
  │                               │
  └── cancelled (hold expired)    └── admin_cancelled / refunded / no_show
```

### Pricing Engine

`services/pricing.py` evaluates `PricingRule` rows highest-priority-first. First matching rule wins.

Each rule can condition on:
- `court_id` / `court_type_id` — specific court or type
- `membership_tier_id` — only applies when user holds this tier
- `weekdays` — comma-separated ISO weekday numbers (0=Mon)
- `date_from` / `date_to` — date range
- `time_from` / `time_to` — slot start window
- `is_holiday` — boolean flag (set by operator on OperatingSchedule)

`amount_cents` is the actual charge; `original_amount_cents` is the strikethrough price shown in the UI.

### Membership System

`MembershipTier` supports four scopes:

| Scope | Applies to |
|---|---|
| `organization` | All venues in the org |
| `venue` | One specific venue |
| `court_type` | All courts of a named type |
| `court` | One specific court |

When a user holds an active `UserMembership`, the pricing engine matches `PricingRule` rows keyed on `membership_tier_id` to apply discounted pricing. Benefits also include an extended `booking_window_days` (advance booking window) and optional `monthly_hour_quota`.

### API Reference

Full OpenAPI docs available at `/docs` in non-production environments.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/wechat` | — | WeChat OAuth login → JWT |
| `GET` | `/api/v1/venues` | optional | List venues (filter: city, is_partner) |
| `GET` | `/api/v1/venues/{id}/availability` | optional | Court × slot grid for a date; includes `courts` metadata with `is_indoor` |
| `POST` | `/api/v1/bookings/hold` | ✓ | Reserve a slot (5-min hold) |
| `POST` | `/api/v1/bookings/confirm` | ✓ | Convert hold to confirmed after payment |
| `GET` | `/api/v1/memberships/tiers` | — | List tiers (filter: venue_id, court_id) |
| `POST` | `/api/v1/memberships/join` | ✓ | Purchase / join a tier |
| `GET` | `/api/v1/memberships/my` | ✓ | Caller's active memberships |
| `POST` | `/api/v1/memberships/{id}/cancel` | ✓ | Cancel a membership |

---

## Frontend — courtflow-app

Built with **uni-app + Vue 3 + TypeScript**, compiled to WeChat Mini Program (primary) and H5.

### Page Structure

```
Tab pages (always loaded):
  /pages/index/index     Home — hero stats, nearby venues, coaches, upcoming bookings
  /pages/courts/index    Courts — browse & quick-book with indoor/outdoor filter, membership strip
  /pages/courses/index   Courses & Coaches — coach cards, lesson packages
  /pages/my/index        Profile — player attributes, booking history, membership status
  /pages/login/index     WeChat OAuth + phone verification

Sub-packages (lazy loaded):
  /packages/venue/detail         Venue detail + booking grid (court × time slot)
  /packages/venue/list           Full venue list with map
  /packages/booking/order        Order review + coupon + pay
  /packages/booking/result       Booking confirmation
  /packages/account/orders       Order history
  /packages/account/profile      Edit profile
  /packages/coach/profile        Coach detail + booking
  /packages/membership/join      Membership purchase flow
```

### Design System

All design tokens live in `src/uni.scss` and are shared across every page.

**Color palette:**

| Token | Value | Usage |
|---|---|---|
| `$cf-bg` | `#080e0b` | Page background (near-black, green soul) |
| `$cf-lime` | `#B8D430` | Primary neon accent — prices, active states, CTAs |
| `$cf-green` | `#2D8B57` | Brand green — gradient start, outdoor courts |
| `$cf-blue` | `#2E86C1` | Brand blue — gradient end, indoor courts |
| `$cf-success` | `#34d399` | Availability indicators, confirmed states |
| `$cf-amber` | `#FBBF24` | Peak-hour slots, ratings |
| `$cf-violet` | `#7B4FA0` | Coaching / courses accent |

**Key patterns:**
- **Glassmorphic cards** — `rgba(255,255,255,0.07)` background + `blur(12-20px)` backdrop filter + `0.5px` border
- **Mesh gradient background** — 4-stop radial gradient with `meshBreathe` animation shared across all tab pages
- **Sticky frosted header** — `rgba(8,14,11,0.88)` + `blur(20px) saturate(1.3)` for all list pages
- **Indoor/outdoor colour system** — blue (`#63b3ed`) for indoor, green (`$cf-success`) for outdoor; applied to badges, tints, and filter states

### State Management

```
stores/auth.ts     — user session (JWT, openid, profile)
stores/booking.ts  — selected date, held slots, active order
```

---

## Getting Started

### Backend

```bash
cd courtflow-api

# Create and activate virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env   # fill in DATABASE_URL, REDIS_URL, JWT_SECRET, etc.

# Run migrations
alembic upgrade head

# Seed development data
python seeds/seed_dev.py

# Start API server
uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

### Frontend

```bash
cd courtflow-app

npm install

# WeChat Mini Program (requires WeChat DevTools)
npm run dev:mp-weixin

# H5 browser preview
npm run dev:h5
```

---

## Roadmap

| Phase | Features |
|---|---|
| **Phase 1** ✅ | Court discovery, real-time booking grid, hold/confirm/cancel, dynamic pricing, discount system, WeChat auth, order flow |
| **Phase 1.5** ✅ | Membership tiers (court/venue/org scoped), UserMembership join/cancel, indoor/outdoor differentiation, availability endpoint enriched with court metadata |
| **Phase 2** 🔜 | Coaching profiles + lesson booking, course packages, training history, AI match analysis |
| **Phase 3** 🔜 | Energy points gamification, social features (open matches, PK challenges), equipment marketplace |
| **Phase 4** 🔜 | Operator dashboard (pricing admin, schedule management, member CRM), analytics |

---

## License

MIT
