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
- [Admin — courtflow-admin](#admin--courtflow-admin)
  - [Admin Page Structure](#admin-page-structure)
  - [Admin API Layer](#admin-api-layer)
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
│   courtflow-app (consumer)  ·  courtflow-admin (org)     │
│              uni-app / Vue 3 / TypeScript                │
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
│   │   ├── api/
│   │   │   ├── v1/endpoints/  # auth · venues · bookings · orders · memberships
│   │   │   └── admin/endpoints/ # organizations · venues · courts · pricing · memberships
│   │   ├── core/           # config · database · security · deps
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── services/       # booking · pricing · availability
│   │   └── tasks/          # ARQ background jobs (hold expiry)
│   ├── scripts/            # init_db.py (create tables + seed)
│   ├── seeds/              # Dev data seeding
│   ├── docker-compose.yml  # PostgreSQL 16 + Redis 7
│   ├── tests/
│   ├── DESIGN.md           # Full architecture & design document
│   └── requirements.txt
│
├── courtflow-app/          # uni-app frontend (consumer-facing)
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
├── courtflow-admin/        # uni-app frontend (org & coach management)
│   └── src/
│       ├── pages/          # Tab pages (dashboard · venues · bookings · pricing · my · login)
│       ├── packages/       # Sub-pages
│       │   ├── org/        # Organization profile editor
│       │   ├── venue/      # Venue CRUD · courts · court-photos · photos · facilities
│       │   ├── booking/    # Booking list & detail with status actions
│       │   ├── pricing/    # Pricing rule editor
│       │   └── membership/ # Membership tier list & editor
│       ├── components/ui/  # CfIcon · CfTabBar · CfCard · CfButton · CfFormItem
│       │                   # CfModal · CfImageUpload · CfEmpty
│       ├── stores/         # Pinia: auth · org
│       ├── api/            # Admin API client (organizations · venues · courts
│       │                   #   court-media · reservations · pricing · memberships)
│       ├── types/          # TypeScript interfaces (full admin types)
│       └── uni.scss        # Shared design system tokens
│
├── UNI_APP_PRODUCT_PLAN.md # Product requirements & competitive analysis
└── README.md
```

---

## Backend — courtflow-api

### Module Map

```
app/
├── api/
│   ├── v1/endpoints/
│   │   ├── auth.py          # POST /auth/wechat-login · POST /auth/phone-login · POST /auth/refresh
│   │   ├── venues.py        # GET /venues · GET /venues/{id} · GET /venues/{id}/availability
│   │   ├── bookings.py      # POST /bookings/hold · POST /bookings/confirm · DELETE /bookings/{id}
│   │   ├── orders.py        # POST /orders · GET /orders/{id} · POST /orders/{id}/pay
│   │   ├── memberships.py   # GET /memberships/tiers · POST /memberships/join
│   │   │                    # GET /memberships/my · POST /memberships/{id}/cancel
│   │   └── users.py         # GET/PUT /users/me
│   │
│   └── admin/endpoints/
│       ├── organizations.py # GET/PUT /admin/organization · members · dashboard stats
│       ├── venues.py        # CRUD /admin/venues + media + facilities
│       ├── courts.py        # CRUD /admin/venues/{id}/courts + court-types + court-media
│       ├── reservations.py  # List/detail/cancel/check-in/no-show/complete reservations
│       ├── court_blocks.py  # CRUD /admin/venues/{id}/courts/{cid}/blocks
│       ├── pricing.py       # CRUD /admin/pricing-rules
│       └── memberships.py   # CRUD /admin/membership-tiers
│
├── core/
│   ├── config.py        # Pydantic Settings (env-based)
│   ├── database.py      # AsyncSession factory + Base
│   ├── security.py      # JWT encode/decode · refresh token hashing
│   └── deps.py          # get_current_user · get_current_user_optional · get_current_admin_user
│
├── models/
│   ├── organization.py  # Organization · MembershipTier · UserMembership · OrganizationMember
│   ├── venue.py         # Venue · VenueMedia · VenueFacility
│   ├── court.py         # Court · CourtType · CourtBlock · CourtLink · CourtMedia
│   ├── reservation.py   # Reservation (hold → confirm → complete)
│   ├── order.py         # Order · OrderItem
│   ├── pricing.py       # PricingRule
│   ├── discount.py      # Discount (coupon/promo/auto)
│   ├── payment.py       # Payment · PaymentAccount
│   ├── schedule.py      # OperatingSchedule (weekday defaults + date overrides)
│   ├── audit.py         # AuditLog (immutable audit trail)
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
└── Venue  (location, hours, timezone)
    ├── Court  (surface, is_indoor, slot_duration_minutes, sort_order)
    │   ├── CourtMedia   (photos, banners, thumbnails)
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

**Consumer API** (`/api/v1/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/wechat-login` | — | WeChat OAuth login → JWT |
| `POST` | `/auth/phone-login` | — | Phone + SMS code login → JWT (admin app) |
| `POST` | `/auth/refresh` | — | Refresh token rotation |
| `GET` | `/venues` | optional | List venues (filter: city, is_partner) |
| `GET` | `/venues/{id}` | — | Venue detail with photos, facilities, court types |
| `GET` | `/venues/{id}/availability` | optional | Court × slot grid for a date |
| `POST` | `/bookings/hold` | ✓ | Reserve a slot (5-min hold) |
| `POST` | `/bookings/confirm` | ✓ | Convert hold to confirmed after payment |
| `GET` | `/memberships/tiers` | — | List tiers (filter: venue_id, court_id) |
| `POST` | `/memberships/join` | ✓ | Purchase / join a tier |
| `GET/PUT` | `/users/me` | ✓ | Get / update user profile |

**Admin API** (`/api/v1/admin/`) — requires org owner/admin/staff/coach role

| Method | Endpoint | Description |
|---|---|---|
| `GET/PUT` | `/organization` | Get / update org profile |
| `GET` | `/organization/members` | List org members with user info |
| `GET` | `/dashboard/stats` | Aggregate stats (venues, courts, members, rules, tiers) |
| `GET/POST` | `/venues` | List / create venues |
| `GET/PUT/DELETE` | `/venues/{id}` | Venue detail / update / soft-delete |
| `GET/POST/DELETE` | `/venues/{id}/media` | Venue photos management |
| `GET/POST/DELETE` | `/venues/{id}/facilities` | Venue facilities management |
| `GET/POST` | `/venues/{id}/courts` | List / create courts |
| `GET/PUT/DELETE` | `/venues/{id}/courts/{cid}` | Court detail / update / soft-delete |
| `GET/POST/DELETE` | `/venues/{id}/courts/{cid}/media` | Court photos management |
| `GET/POST/DELETE` | `/venues/{id}/courts/{cid}/blocks` | Court maintenance windows |
| `GET/POST` | `/venues/{id}/court-types` | List / create court types |
| `PUT/DELETE` | `/venues/{id}/court-types/{tid}` | Update / delete court type |
| `GET` | `/reservations` | List reservations (filter: venue_id, court_id, date, status, page) |
| `GET` | `/reservations/{id}` | Reservation detail |
| `POST` | `/reservations/{id}/cancel` | Cancel reservation (with optional reason) |
| `POST` | `/reservations/{id}/check-in` | Check in user |
| `POST` | `/reservations/{id}/no-show` | Mark no-show |
| `POST` | `/reservations/{id}/complete` | Complete session |
| `GET/POST` | `/pricing-rules` | List (filter: venue_id, court_type_id) / create |
| `GET/PUT/DELETE` | `/pricing-rules/{id}` | Pricing rule detail / update / delete |
| `GET/POST` | `/membership-tiers` | List / create membership tiers |
| `GET/PUT/DELETE` | `/membership-tiers/{id}` | Tier detail / update / delete |

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

## Admin — courtflow-admin

Built with **uni-app + Vue 3 + TypeScript** (same stack as courtflow-app), this is the management console for organizations and coaches to manage their venue operations.

### Admin Page Structure

```
Tab pages:
  /pages/index/index       Dashboard — org overview stats, quick actions
  /pages/venues/index      Venue list — browse, create, manage venues
  /pages/bookings/index    Bookings — view, filter (venue/status/date), manage all reservations
  /pages/pricing/index     Pricing rules — list, create, edit rules
  /pages/my/index          Profile — account settings, org info, logout
  /pages/login/index       Phone + SMS verification login

Sub-packages:
  /packages/org/profile          Edit org name, logo, description
  /packages/venue/edit           Create / edit venue (address, hours, contact)
  /packages/venue/courts         Court list for a venue
  /packages/venue/court-detail   Court detail (photos, pricing rules, blocks, recent bookings)
  /packages/venue/court-edit     Create / edit court (name, surface, indoor/outdoor)
  /packages/venue/court-photos   Manage court photos (add, delete, preview)
  /packages/venue/photos         Manage venue photos
  /packages/venue/facilities     Manage venue facilities (parking, showers, etc.)
  /packages/booking/list         Booking list (filtered by venue/court, navigated from court detail)
  /packages/booking/detail       Booking detail with actions (check-in, complete, cancel, no-show)
  /packages/pricing/edit         Create / edit pricing rule (weekday, time, priority)
  /packages/membership/list      Membership tier list
  /packages/membership/edit      Create / edit tier (scope, price, duration, benefits)
```

### Admin API Layer

All admin endpoints use the `/api/v1/admin/` prefix and require an authenticated user with org owner/admin/staff role.

| Module | Endpoints |
|---|---|
| **Organization** | `GET/PUT /admin/organization` · `GET /admin/organization/members` · `GET /admin/dashboard/stats` |
| **Venues** | `GET/POST /admin/venues` · `GET/PUT/DELETE /admin/venues/{id}` |
| **Venue Media** | `GET/POST /admin/venues/{id}/media` · `DELETE /admin/venues/{id}/media/{mediaId}` |
| **Venue Facilities** | `GET/POST /admin/venues/{id}/facilities` · `DELETE /admin/venues/{id}/facilities/{fid}` |
| **Courts** | `GET/POST /admin/venues/{id}/courts` · `GET/PUT/DELETE /admin/venues/{id}/courts/{cid}` |
| **Court Media** | `GET/POST /admin/venues/{id}/courts/{cid}/media` · `DELETE /admin/venues/{id}/courts/{cid}/media/{mid}` |
| **Court Blocks** | `GET/POST /admin/venues/{id}/courts/{cid}/blocks` · `DELETE /admin/venues/{id}/courts/{cid}/blocks/{bid}` |
| **Court Types** | `GET/POST /admin/venues/{id}/court-types` · `PUT/DELETE /admin/venues/{id}/court-types/{tid}` |
| **Reservations** | `GET /admin/reservations` · `GET /admin/reservations/{id}` · `POST .../cancel` · `POST .../check-in` · `POST .../no-show` · `POST .../complete` |
| **Pricing Rules** | `GET/POST /admin/pricing-rules` · `GET/PUT/DELETE /admin/pricing-rules/{id}` |
| **Membership Tiers** | `GET/POST /admin/membership-tiers` · `GET/PUT/DELETE /admin/membership-tiers/{id}` |

### Admin UI Components

Extends the shared design system with admin-specific components:

| Component | Purpose |
|---|---|
| `CfCard` | Glass card container with optional title + action slot |
| `CfButton` | Primary / secondary / danger / ghost buttons with icon support |
| `CfFormItem` | Label + input wrapper with required indicator, hint, and error |
| `CfModal` | Confirmation / dialog modal with customizable footer |
| `CfImageUpload` | Multi-image upload with preview and removal |
| `CfEmpty` | Empty state placeholder with icon and text |

---

## Getting Started

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** with npm
- **Docker** (for PostgreSQL and Redis) — or install them natively

### 1. Start Infrastructure

```bash
cd courtflow-api

# Start PostgreSQL 16 + Redis 7 via Docker
docker compose up -d
```

This creates:
- PostgreSQL at `localhost:5432` (user: `courtflow`, password: `courtflow`, db: `courtflow`)
- Redis at `localhost:6379`

### 2. Start Backend

```bash
cd courtflow-api

# Create and activate virtual environment
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create tables and seed dev data (first time only)
python -m scripts.init_db

# Start API server
python -m uvicorn app.main:app --reload --port 8000
```

The `.env` file is pre-configured for local development. API docs at `http://localhost:8000/docs`.

The dev seed creates:
- Organization "瑛赛网球" with one venue (3 courts, pricing rules)
- Test user (phone: `19195233697`) as org owner — use this to log into the admin console

#### Database Migration

When new models are added (e.g. `CourtMedia`), run the migration script to create the new tables without re-seeding:

```bash
cd courtflow-api
python -m scripts.migrate
```

| Script | What it does | When to use |
|---|---|---|
| `python -m scripts.init_db` | Creates all tables **+ seeds dev data** | First-time setup only |
| `python -m scripts.migrate` | Creates only new/missing tables (existing data untouched) | After pulling new model changes |

### 3. Start Admin Console

```bash
cd courtflow-admin

npm install

# H5 browser preview (port 5174, proxies /api/* to localhost:8000)
npm run dev:h5
```

Open `http://localhost:5174` → log in with phone `19195233697` and any verification code (dev mode skips SMS).

### 4. Start Consumer App (optional)

```bash
cd courtflow-app

npm install

# H5 browser preview
npm run dev:h5

# WeChat Mini Program (requires WeChat DevTools)
npm run dev:mp-weixin
```

### Dev Environment Overview

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────┐
│ courtflow-   │     │   courtflow-api  │     │  PostgreSQL  │
│ admin :5174  │────▶│     :8000        │────▶│    :5432     │
│ (Vite proxy) │     │   (FastAPI)      │     └─────────────┘
└──────────────┘     │                  │     ┌─────────────┐
┌──────────────┐     │                  │────▶│   Redis      │
│ courtflow-   │────▶│                  │     │    :6379     │
│ app   :5173  │     └──────────────────┘     └─────────────┘
└──────────────┘
```

---

## Roadmap

| Phase | Features |
|---|---|
| **Phase 1** ✅ | Court discovery, real-time booking grid, hold/confirm/cancel, dynamic pricing, discount system, WeChat auth, order flow |
| **Phase 1.5** ✅ | Membership tiers (court/venue/org scoped), UserMembership join/cancel, indoor/outdoor differentiation, availability endpoint enriched with court metadata |
| **Phase 1.6** ✅ | Admin console frontend (`courtflow-admin`) — org profile, venue/court CRUD, pricing rules, membership tier management |
| **Phase 1.7** ✅ | Admin API backend (35 endpoints), phone login, admin auth dependency, per-court slot duration, frontend↔backend integration with dev proxy |
| **Phase 1.8** ✅ | Court photos (CourtMedia model + CRUD API + admin UI), bookings tab (venue/status/date filters, pagination, reservation management) |
| **Phase 2** 🔜 | S3 image upload, SMS verification (production), coaching profiles + lesson booking |
| **Phase 3** 🔜 | Energy points gamification, social features (open matches, PK challenges), equipment marketplace |
| **Phase 4** 🔜 | Analytics dashboard, member CRM, advanced scheduling, AI match analysis |

---

## License

MIT
