# RallyAI -- Tennis Court Reservation Platform: Design Document

**Version:** 1.2
**Date:** 2026-03-13
**Status:** Draft

---

## Table of Contents

1. System Architecture Overview
2. Tech Stack Recommendation
3. Multi-Tenancy Strategy
4. Database Schema Design
5. Authentication and Authorization
6. API Endpoint Design
7. Reservation and Booking Engine
8. Payment Flow
9. Pricing and Discount Engine
10. Time Zone Handling
11. Extensibility Design
12. Performance and Scaling Considerations
13. Edge Cases and Failure Modes

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
                          +------------------+
                          |   CDN (Assets)   |
                          +--------+---------+
                                   |
                 +-----------------+-----------------+
                 |        API Gateway / LB           |
                 |  (rate limiting, SSL, routing)     |
                 +-----------------+-----------------+
                          |                |
              +-----------+--+      +------+----------+
              | Public API   |      | Admin API       |
              | (Next.js BFF)|      | (Next.js BFF)   |
              +------+-------+      +------+----------+
                     |                     |
                     +----------+----------+
                                |
                     +----------+----------+
                     |   Application Core  |
                     |  (FastAPI / Python)  |
                     +----+-----+-----+---+
                          |     |     |
              +-----------+  +--+--+  +-----------+
              |              |     |              |
        +-----+----+  +-----+--+ +----+-----+ +--+--------+
        | PostgreSQL|  |  Redis  | |  S3/Blob | | Stripe/   |
        | (Primary) |  | (Cache, | | (Media)  | | Payment   |
        |           |  |  Queue) | |          | | Gateway)  |
        +-----------+  +--------+ +----------+ +----------+
```

### 1.2 Design Principles

- **Shared-database, shared-schema multi-tenancy** with a `org_id` discriminator column on all tenant-scoped tables. This is the right tradeoff for a platform targeting 10k+ users across dozens-to-hundreds of organizations: simpler ops than database-per-tenant, adequate isolation via row-level security.
- **Domain-driven module boundaries**: Booking, Pricing, Payment, Identity, and Organization modules are separated at the code level to allow independent evolution.
- **Optimistic concurrency with database-level locking** for reservation slot claims to prevent double-booking.
- **Event-driven side effects**: Booking confirmation, payment capture, notification dispatch happen through an internal event bus (Redis Streams or Celery/ARQ), keeping the critical path fast.

---

## 2. Tech Stack Recommendation

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **API Server** | **FastAPI** (Python 3.12+) | Async-native, auto-generated OpenAPI docs, Pydantic validation, dependency injection, high performance for Python |
| **Database** | **PostgreSQL 16** | Row-level security for tenant isolation; JSONB for flexible metadata; robust locking primitives; excellent indexing (GIN, partial, composite) |
| **ORM** | **SQLAlchemy 2.0** + **Alembic** | Mature async support, powerful query builder, battle-tested migrations; or **SQLModel** for FastAPI-native Pydantic integration |
| **Cache / Queue** | **Redis 7** + **Celery** (or **ARQ** for async-native) | Slot availability caching; background job processing (emails, payment reconciliation, expiring held slots) |
| **Auth** | **Custom JWT** + **Refresh Tokens** (via **python-jose** + **passlib**) | Multi-role, multi-tenant claims in JWT; refresh token rotation |
| **Payments** | **Stripe Connect** (Express accounts) | Each organization is a connected account; platform takes configurable commission; handles refunds, disputes |
| **Object Storage** | **AWS S3** or **Cloudflare R2** (via **boto3**) | Organization logos, court photos, user avatars |
| **Frontend (User)** | **Next.js 14+ (App Router)** | SSR for SEO on public pages; dynamic theming via CSS variables per organization; React Server Components for performance |
| **Frontend (Admin)** | **Next.js** shared codebase, separate route group | Organization admin dashboard; platform admin super-panel |
| **Hosting** | **AWS** (ECS Fargate or EC2) or **Vercel** (frontend) + **Railway/Render** (API) | Scales horizontally; managed Postgres (RDS/Supabase/Neon) |
| **Monitoring** | **Sentry** (errors), **Axiom or Datadog** (logs/metrics) | Production observability |
| **API Schema Sync** | **openapi-typescript-codegen** | Auto-generate TypeScript client from FastAPI's OpenAPI spec to bridge Python backend and Next.js frontend types |

---

## 3. Multi-Tenancy Strategy

### 3.1 Approach: Shared Schema with Row-Level Security

Every tenant-scoped table carries a `org_id UUID NOT NULL` column. PostgreSQL Row-Level Security (RLS) policies enforce isolation at the database level as a defense-in-depth measure, while application-level middleware injects organization context from the authenticated session.

```sql
-- Example RLS policy (applied per-table)
ALTER TABLE courts ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON courts
  USING (org_id = current_setting('app.current_org_id')::uuid);
```

### 3.2 Tenant Resolution

- **User-facing**: Organization is identified by subdomain (`acme.rallyai.com`) or custom domain (`book.acmetennis.com`). The `organization_domains` table maps hostnames to `org_id`.
- **Admin-facing**: Authenticated session carries `org_id` claim in JWT.
- **Platform admin**: Special role that can set `org_id` context to any tenant or operate cross-tenant.

### 3.3 Data Isolation Boundaries

| Data | Isolation Level |
|------|----------------|
| Users | **Shared** -- a user can book at multiple organizations. `organization_members` join table tracks per-organization membership, roles, and tiers. |
| Courts, Schedules, Pricing | **Strictly tenant-scoped** via `org_id` |
| Reservations | **Tenant-scoped** but user-linked across tenants |
| Payments | **Tenant-scoped**; Stripe Connected Account per organization |

---

## 4. Database Schema Design


### 4.1 Entity Relationship Overview

```
users --< organization_members >-- organizations
              |                          |
        membership_tiers    +------------+------------+
                            |            |            |
                          courts    schedules    pricing_rules
                            |            |            |
                            +-----+------+            |
                                  |                   |
                             time_slots --------------+
                                  |
                             reservations ---- payments
                                  |
                             reservation_slots
```

**Relationships:**
- `users` M:N `organizations` (via `organization_members` join table with roles + tiers)
- `organization_members` N:1 `membership_tiers` (optional tier per membership)
- `organizations` 1:N `courts`, `operating_schedules`, `pricing_rules`, `discounts`, `membership_tiers`
- `courts` 1:N `reservations`, `court_blocks`
- `reservations` 1:1 `payments`
- `reservations` N:1 `users`, `courts`, `discounts`


### 4.2 Complete Table Definitions

#### 4.2.1 `users`

Global user table (not tenant-scoped).

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE,
    phone           VARCHAR(20) UNIQUE,
    password_hash   VARCHAR(255),           -- nullable if social login only
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    avatar_url      VARCHAR(500),
    locale          VARCHAR(10) DEFAULT 'en',
    email_verified  BOOLEAN DEFAULT FALSE,
    phone_verified  BOOLEAN DEFAULT FALSE,
    is_platform_admin BOOLEAN DEFAULT FALSE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- At least one of email or phone must be present
    CONSTRAINT chk_user_contact CHECK (email IS NOT NULL OR phone IS NOT NULL)
);

CREATE INDEX idx_users_email ON users (email) WHERE email IS NOT NULL;
CREATE INDEX idx_users_phone ON users (phone) WHERE phone IS NOT NULL;
```

#### 4.2.2 `organizations`

```sql
CREATE TABLE organizations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(200) NOT NULL,
    slug                VARCHAR(100) UNIQUE NOT NULL,   -- used in URLs
    description         TEXT,
    logo_url            VARCHAR(500),
    cover_image_url     VARCHAR(500),
    timezone            VARCHAR(50) NOT NULL,            -- e.g. 'Asia/Shanghai', 'America/New_York'
    default_currency    CHAR(3) NOT NULL DEFAULT 'USD',  -- ISO 4217
    country_code        CHAR(2) NOT NULL,                -- ISO 3166-1 alpha-2
    address_line1       VARCHAR(300),
    address_line2       VARCHAR(300),
    city                VARCHAR(100),
    state_province      VARCHAR(100),
    postal_code         VARCHAR(20),
    latitude            DECIMAL(10, 7),
    longitude           DECIMAL(10, 7),
    phone               VARCHAR(20),
    email               VARCHAR(255),
    website_url         VARCHAR(500),

    -- Booking defaults (courts inherit these; can override per-court)
    default_slot_duration_mins  INT NOT NULL DEFAULT 60,      -- 30 or 60 typical
    advance_booking_days        INT NOT NULL DEFAULT 7,       -- how far ahead users can book
    min_advance_booking_mins    INT NOT NULL DEFAULT 60,      -- minimum notice
    cancellation_policy_hours   INT NOT NULL DEFAULT 24,      -- free cancellation window
    cancellation_fee_percent    DECIMAL(5,2) DEFAULT 0,       -- fee if within window
    allow_recurring             BOOLEAN DEFAULT FALSE,

    -- Platform
    platform_fee_percent        DECIMAL(5,2) DEFAULT 5.00,    -- RallyAI's cut

    -- Status
    status              VARCHAR(20) NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active','suspended','onboarding','archived')),
    is_verified         BOOLEAN DEFAULT FALSE,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_organizations_slug ON organizations (slug);
CREATE INDEX idx_organizations_status ON organizations (status) WHERE status = 'active';
CREATE INDEX idx_organizations_geo ON organizations (latitude, longitude) WHERE latitude IS NOT NULL;
```

#### 4.2.3 `organization_themes`

```sql
CREATE TABLE organization_themes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    primary_color   VARCHAR(7) NOT NULL DEFAULT '#6B46C1',  -- hex
    secondary_color VARCHAR(7) NOT NULL DEFAULT '#FFFFFF',
    accent_color    VARCHAR(7),
    text_color      VARCHAR(7) DEFAULT '#1A1A1A',
    bg_color        VARCHAR(7) DEFAULT '#FFFFFF',
    font_family     VARCHAR(100) DEFAULT 'Inter',
    border_radius   VARCHAR(10) DEFAULT '8px',
    custom_css      TEXT,                                    -- advanced override
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_org_theme UNIQUE (org_id)
);
```

#### 4.2.4 `organization_domains`

```sql
CREATE TABLE organization_domains (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    domain      VARCHAR(255) UNIQUE NOT NULL,   -- e.g. 'acme.rallyai.com' or 'book.acme.com'
    is_primary  BOOLEAN DEFAULT FALSE,
    verified    BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_organization_domains_domain ON organization_domains (domain);
```

#### 4.2.5 `organization_members` (Membership, Roles & Tiers)

A user's relationship with an organization has two orthogonal dimensions:
- **Role** — what the user can **do** (permissions): `owner`, `admin`, `manager`, `staff`, `member`
- **Tier** — what the user **gets** (benefits): linked to `membership_tiers`, nullable (NULL = free/default)

This allows a single user to be an admin at one organization, a paid premium member at another, and a free member at a third.

```sql
CREATE TABLE organization_members (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- ACCESS: what can this user DO within the org
    role        VARCHAR(20) NOT NULL DEFAULT 'member'
                CHECK (role IN ('owner','admin','manager','staff','member')),

    -- BENEFITS: what does this user GET (NULL = free/no tier)
    tier_id     UUID REFERENCES membership_tiers(id) ON DELETE SET NULL,

    -- STATUS
    status      VARCHAR(20) NOT NULL DEFAULT 'active'
                CHECK (status IN ('active','invited','suspended','removed')),

    -- Metadata
    loyalty_points      INT DEFAULT 0,
    notes               TEXT,                        -- staff notes about this person
    invited_by          UUID REFERENCES users(id),
    joined_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_org_member UNIQUE (org_id, user_id)
);

CREATE INDEX idx_org_members_user ON organization_members (user_id);
CREATE INDEX idx_org_members_org_role ON organization_members (org_id, role);
CREATE INDEX idx_org_members_tier ON organization_members (tier_id) WHERE tier_id IS NOT NULL;
```

#### 4.2.6 `membership_tiers` (Per-Organization Benefit Levels)

Each organization defines its own set of membership tiers. Tiers control booking benefits (priority, discounts, advance booking windows) and are independent of roles.

```sql
CREATE TABLE membership_tiers (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id                  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name                    VARCHAR(100) NOT NULL,          -- 'Free', 'Basic', 'Premium', 'VIP'
    slug                    VARCHAR(50) NOT NULL,           -- 'free', 'basic', 'premium', 'vip'
    description             TEXT,
    price                   DECIMAL(10,2) NOT NULL DEFAULT 0,
    currency                CHAR(3) NOT NULL DEFAULT 'USD',
    billing_interval        VARCHAR(10)
                            CHECK (billing_interval IN ('monthly','quarterly','yearly','one_time')),
    benefits                JSONB DEFAULT '{}'::jsonb,      -- {"free_bookings_per_month": 4, "guest_passes": 2}
    booking_priority        INT DEFAULT 0,                  -- higher = earlier booking window
    discount_percent        DECIMAL(5,2) DEFAULT 0,         -- auto-discount on bookings
    max_advance_booking_days INT,                           -- override org default (NULL = use org default)
    sort_order              INT DEFAULT 0,
    is_default              BOOLEAN DEFAULT FALSE,          -- auto-assigned on join (the "free" tier)
    is_active               BOOLEAN DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_tier_slug UNIQUE (org_id, slug)
);

CREATE INDEX idx_tiers_org ON membership_tiers (org_id, is_active, sort_order);
```

#### 4.2.7 `courts`

```sql
CREATE TABLE courts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,          -- "Court 1", "Center Court"
    description     TEXT,
    surface_type    VARCHAR(30) NOT NULL
                    CHECK (surface_type IN ('hard','clay','grass','carpet','artificial','other')),
    court_type      VARCHAR(30) NOT NULL DEFAULT 'outdoor'
                    CHECK (court_type IN ('indoor','outdoor','covered')),
    is_doubles      BOOLEAN DEFAULT TRUE,            -- singles vs doubles width
    has_lighting    BOOLEAN DEFAULT TRUE,
    max_players     INT DEFAULT 4,
    image_urls      JSONB DEFAULT '[]'::jsonb,       -- array of image URLs
    amenities       JSONB DEFAULT '[]'::jsonb,       -- ["water_fountain","seating","scoreboard"]
    sort_order      INT DEFAULT 0,                   -- display order

    -- Booking config (NULL = inherit from organization defaults)
    slot_duration_mins          INT,                 -- 30 or 60 typical; NULL = org default
    advance_booking_days        INT,                 -- how far ahead; NULL = org default
    min_advance_booking_mins    INT,                 -- minimum notice; NULL = org default
    cancellation_policy_hours   INT,                 -- free cancellation window; NULL = org default
    cancellation_fee_percent    DECIMAL(5,2),        -- fee if within window; NULL = org default

    -- Base pricing (fallback when no pricing_rule matches)
    base_price_per_slot         DECIMAL(10,2),       -- default price per slot; NULL = must have pricing_rules
    currency                    CHAR(3),             -- NULL = org default_currency

    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','maintenance','inactive')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_courts_org ON courts (org_id, status);
CREATE INDEX idx_courts_org_sort ON courts (org_id, sort_order);
```

#### 4.2.8 `operating_schedules`

Defines when an organization/court is open. Uses a day-of-week recurring model with override capability for holidays and special dates.

```sql
CREATE TABLE operating_schedules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    court_id        UUID REFERENCES courts(id) ON DELETE CASCADE,  -- NULL = applies to all courts
    day_of_week     SMALLINT,                  -- 0=Sunday..6=Saturday; NULL for specific-date override
    specific_date   DATE,                      -- non-null for date-specific override (holiday, event)
    open_time       TIME NOT NULL,             -- in organization's local timezone
    close_time      TIME NOT NULL,
    is_closed       BOOLEAN DEFAULT FALSE,     -- TRUE = explicitly closed this day/date
    label           VARCHAR(100),              -- "Holiday", "Tournament", etc.
    priority        INT DEFAULT 0,             -- higher priority overrides lower
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_schedule_day CHECK (day_of_week IS NOT NULL OR specific_date IS NOT NULL),
    CONSTRAINT chk_schedule_times CHECK (is_closed = TRUE OR open_time < close_time)
);

CREATE INDEX idx_schedules_org_day ON operating_schedules (org_id, day_of_week)
    WHERE specific_date IS NULL;
CREATE INDEX idx_schedules_org_date ON operating_schedules (org_id, specific_date)
    WHERE specific_date IS NOT NULL;
CREATE INDEX idx_schedules_court ON operating_schedules (court_id)
    WHERE court_id IS NOT NULL;
```

#### 4.2.9 `court_blocks` (Maintenance Windows / Manual Locks)

```sql
CREATE TABLE court_blocks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    court_id        UUID NOT NULL REFERENCES courts(id) ON DELETE CASCADE,
    start_at        TIMESTAMPTZ NOT NULL,
    end_at          TIMESTAMPTZ NOT NULL,
    reason          VARCHAR(50) NOT NULL
                    CHECK (reason IN ('maintenance','tournament','private_event','weather','other')),
    notes           TEXT,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_block_times CHECK (start_at < end_at)
);

CREATE INDEX idx_court_blocks_lookup ON court_blocks (court_id, start_at, end_at);
CREATE INDEX idx_court_blocks_org ON court_blocks (org_id, start_at);
```

#### 4.2.10 `pricing_rules`

Defines time-of-day and day-of-week pricing per court. Rules are evaluated in priority order; first match wins, falling back to `courts.base_price_per_slot` if no rule matches.

From the reference apps, typical patterns:
- Court 1: ¥118 morning (07:00-10:00), ¥148 peak (10:00-22:00)
- Court 2: ¥35 daytime (08:00-17:00), ¥50 evening (17:00-20:00), ¥100 night (20:00-22:00)
- Weekend prices higher than weekday for the same time band

```sql
CREATE TABLE pricing_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    court_id            UUID REFERENCES courts(id) ON DELETE CASCADE,    -- NULL = all courts in org
    name                VARCHAR(100) NOT NULL,       -- "Weekday Peak", "Weekend Morning"

    -- Temporal conditions (all in organization's local timezone)
    day_of_week         SMALLINT[],             -- e.g. {1,2,3,4,5} for weekdays; NULL = all days
    start_time          TIME,                   -- slot start must be >= this; NULL = from open
    end_time            TIME,                   -- slot start must be < this; NULL = until close
    valid_from          DATE,                   -- seasonal pricing start; NULL = always
    valid_until         DATE,                   -- seasonal pricing end; NULL = always

    -- Price
    price_per_slot      DECIMAL(10,2) NOT NULL, -- actual price per slot
    list_price_per_slot DECIMAL(10,2),          -- original/strikethrough price for display (NULL = no strikethrough)
    currency            CHAR(3) NOT NULL DEFAULT 'USD',

    -- Classification
    tier                VARCHAR(20) DEFAULT 'standard'
                        CHECK (tier IN ('off_peak','standard','peak','premium','super_peak')),
    priority            INT NOT NULL DEFAULT 0,  -- higher wins on conflict

    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_pricing_org ON pricing_rules (org_id, is_active, priority DESC);
CREATE INDEX idx_pricing_court ON pricing_rules (court_id) WHERE court_id IS NOT NULL;
```

**Price resolution order:**
1. Find all active `pricing_rules` matching this court (or `court_id IS NULL`), day, and time
2. Sort by `priority DESC`; first match wins
3. If no rule matches, fall back to `courts.base_price_per_slot`
4. If neither exists, the slot is not bookable (configuration error)
5. Member tier discounts (`membership_tiers.discount_percent`) are applied on top of the resolved price

#### 4.2.11 `discounts`

```sql
CREATE TABLE discounts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    code                VARCHAR(50),                 -- promo code; NULL if auto-applied
    name                VARCHAR(100) NOT NULL,
    description         TEXT,
    discount_type       VARCHAR(20) NOT NULL
                        CHECK (discount_type IN ('percentage','fixed_amount','time_extension')),
    discount_value      DECIMAL(10,2) NOT NULL,      -- percent or fixed amount
    min_booking_amount  DECIMAL(10,2),               -- minimum subtotal to qualify
    max_discount_amount DECIMAL(10,2),               -- cap for percentage discounts
    applicable_courts   UUID[],                      -- NULL = all courts
    applicable_days     SMALLINT[],                  -- NULL = all days
    applicable_times    JSONB,                       -- {"start": "06:00", "end": "09:00"}

    -- Usage limits
    max_uses_total      INT,
    max_uses_per_user   INT DEFAULT 1,
    current_uses        INT DEFAULT 0,

    valid_from          TIMESTAMPTZ NOT NULL,
    valid_until         TIMESTAMPTZ NOT NULL,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_discount_code UNIQUE (org_id, code)
);

CREATE INDEX idx_discounts_org_active ON discounts (org_id, is_active)
    WHERE is_active = TRUE;
CREATE INDEX idx_discounts_code ON discounts (org_id, code)
    WHERE code IS NOT NULL AND is_active = TRUE;
```

#### 4.2.12 `reservations`

```sql
CREATE TABLE reservations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES organizations(id),
    user_id             UUID NOT NULL REFERENCES users(id),
    court_id            UUID NOT NULL REFERENCES courts(id),

    -- Time range (stored in UTC)
    start_at            TIMESTAMPTZ NOT NULL,
    end_at              TIMESTAMPTZ NOT NULL,

    -- Denormalized local time for queries (organization timezone)
    local_date          DATE NOT NULL,           -- the date in organization timezone
    local_start_time    TIME NOT NULL,
    local_end_time      TIME NOT NULL,

    -- Pricing snapshot
    subtotal            DECIMAL(10,2) NOT NULL,
    discount_amount     DECIMAL(10,2) DEFAULT 0,
    tax_amount          DECIMAL(10,2) DEFAULT 0,
    total_amount        DECIMAL(10,2) NOT NULL,
    currency            CHAR(3) NOT NULL,
    discount_id         UUID REFERENCES discounts(id),
    pricing_snapshot    JSONB,                   -- frozen pricing details at time of booking

    -- Status machine
    status              VARCHAR(20) NOT NULL DEFAULT 'pending_payment'
                        CHECK (status IN (
                            'held',              -- slot temporarily held during checkout
                            'pending_payment',   -- awaiting payment confirmation
                            'confirmed',         -- paid and confirmed
                            'checked_in',        -- user arrived
                            'completed',         -- session finished
                            'cancelled',         -- cancelled by user
                            'admin_cancelled',   -- cancelled by staff
                            'no_show',           -- user didn't show up
                            'refunded'           -- payment refunded
                        )),

    -- Recurring
    recurrence_rule     JSONB,                   -- {"frequency":"weekly","until":"2026-06-01","day_of_week":3}
    recurrence_group_id UUID,                    -- links recurring instances together
    
    -- Metadata
    notes               TEXT,                    -- user notes ("bringing ball machine")
    player_count        INT DEFAULT 2,
    cancelled_at        TIMESTAMPTZ,
    cancellation_reason TEXT,
    checked_in_at       TIMESTAMPTZ,
    hold_expires_at     TIMESTAMPTZ,             -- for 'held' status

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_reservation_times CHECK (start_at < end_at)
);

-- Critical: prevents double-booking at the database level
CREATE UNIQUE INDEX idx_no_double_booking
    ON reservations (court_id, start_at, end_at)
    WHERE status NOT IN ('cancelled','admin_cancelled','refunded');

-- Alternatively, use an exclusion constraint (requires btree_gist extension):
-- CREATE EXTENSION IF NOT EXISTS btree_gist;
-- ALTER TABLE reservations ADD CONSTRAINT no_overlapping_bookings
--     EXCLUDE USING gist (
--         court_id WITH =,
--         tstzrange(start_at, end_at) WITH &&
--     ) WHERE (status NOT IN ('cancelled','admin_cancelled','refunded'));

CREATE INDEX idx_reservations_org_date ON reservations (org_id, local_date);
CREATE INDEX idx_reservations_court_time ON reservations (court_id, start_at, end_at)
    WHERE status NOT IN ('cancelled','admin_cancelled','refunded');
CREATE INDEX idx_reservations_user ON reservations (user_id, status);
CREATE INDEX idx_reservations_status ON reservations (status, hold_expires_at)
    WHERE status = 'held';
CREATE INDEX idx_reservations_recurrence ON reservations (recurrence_group_id)
    WHERE recurrence_group_id IS NOT NULL;
```

#### 4.2.13 `payment_accounts` (Organization Payment Receiving)

Each organization can connect one or more payment provider accounts. This decouples the platform from any single provider (Stripe, WeChat Pay, Alipay, etc.).

```sql
CREATE TABLE payment_accounts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    provider        VARCHAR(30) NOT NULL,          -- 'stripe', 'wechat_pay', 'alipay', 'paypal'
    account_id      VARCHAR(200) NOT NULL,         -- provider-specific account ID
    account_type    VARCHAR(30),                   -- e.g. 'express', 'standard' for Stripe
    display_name    VARCHAR(100),                  -- "Stripe (Main)", "WeChat Pay"
    is_primary      BOOLEAN DEFAULT FALSE,
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','pending','suspended','disconnected')),
    metadata        JSONB DEFAULT '{}'::jsonb,     -- provider-specific config
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_payment_accounts_org ON payment_accounts (org_id, status);
```

#### 4.2.14 `user_payment_methods`

Stores saved payment methods for users across providers.

```sql
CREATE TABLE user_payment_methods (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider            VARCHAR(30) NOT NULL,          -- 'stripe', 'wechat_pay', 'alipay'
    provider_method_id  VARCHAR(200),                  -- provider's token/method ID
    method_type         VARCHAR(30) NOT NULL,           -- 'card', 'wechat', 'alipay', 'bank_account'
    display_name        VARCHAR(100),                  -- "Visa ending in 4242"
    last4               VARCHAR(4),
    is_default          BOOLEAN DEFAULT FALSE,
    status              VARCHAR(20) NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active','expired','removed')),
    expires_at          TIMESTAMPTZ,
    metadata            JSONB DEFAULT '{}'::jsonb,     -- card brand, bank name, etc.
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_user_payment_methods_user ON user_payment_methods (user_id, status);
```

#### 4.2.15 `payments`

Provider-agnostic payment records. The `provider` + `provider_payment_id` columns replace Stripe-specific fields, allowing each organization to accept payments through different providers.

```sql
CREATE TABLE payments (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id                  UUID NOT NULL REFERENCES organizations(id),
    reservation_id          UUID NOT NULL REFERENCES reservations(id),
    user_id                 UUID NOT NULL REFERENCES users(id),

    -- Amounts
    amount                  DECIMAL(10,2) NOT NULL,
    currency                CHAR(3) NOT NULL,
    platform_fee            DECIMAL(10,2) NOT NULL,     -- RallyAI's take
    org_payout              DECIMAL(10,2) NOT NULL,     -- organization receives

    -- Provider (agnostic)
    provider                VARCHAR(30) NOT NULL,        -- 'stripe', 'wechat_pay', 'alipay'
    provider_payment_id     VARCHAR(200),                -- e.g. Stripe PaymentIntent ID, WeChat transaction ID
    provider_transfer_id    VARCHAR(200),                -- transfer/settlement ID to org account
    payment_account_id      UUID REFERENCES payment_accounts(id),  -- which org account received funds
    payment_method_type     VARCHAR(30),                 -- 'card', 'wechat', 'alipay', etc.
    payment_method_last4    VARCHAR(4),

    status                  VARCHAR(20) NOT NULL DEFAULT 'pending'
                            CHECK (status IN (
                                'pending','processing','succeeded',
                                'failed','refund_pending','refunded',
                                'partially_refunded','disputed'
                            )),

    refund_amount           DECIMAL(10,2) DEFAULT 0,
    refund_reason           TEXT,
    refunded_at             TIMESTAMPTZ,

    paid_at                 TIMESTAMPTZ,
    failed_at               TIMESTAMPTZ,
    failure_reason          TEXT,

    metadata                JSONB DEFAULT '{}'::jsonb,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_payments_reservation ON payments (reservation_id);
CREATE INDEX idx_payments_user ON payments (user_id);
CREATE INDEX idx_payments_org_status ON payments (org_id, status, paid_at);
CREATE INDEX idx_payments_provider ON payments (provider, provider_payment_id)
    WHERE provider_payment_id IS NOT NULL;
```

#### 4.2.16 `refresh_tokens`

```sql
CREATE TABLE refresh_tokens (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash      VARCHAR(128) NOT NULL UNIQUE,
    device_info     VARCHAR(300),
    ip_address      INET,
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens (user_id)
    WHERE revoked_at IS NULL;
```

#### 4.2.17 `audit_log`

```sql
CREATE TABLE audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      UUID REFERENCES organizations(id),
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(50) NOT NULL,       -- 'reservation.created', 'pricing.updated', etc.
    entity_type     VARCHAR(50) NOT NULL,
    entity_id       UUID,
    old_values      JSONB,
    new_values      JSONB,
    ip_address      INET,
    user_agent      VARCHAR(500),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_org ON audit_log (org_id, created_at DESC);
CREATE INDEX idx_audit_entity ON audit_log (entity_type, entity_id);
```

#### 4.2.18 Extensibility Tables (Future -- Schema Only, Not Built Yet)

These tables are defined now so the schema can accommodate future features without migrations that break existing foreign keys.

> **Note:** Membership tiers are now part of the core schema (see 4.2.6 `membership_tiers` and the `tier_id` FK on `organization_members`). Stripe subscription tracking for paid tiers can be added via a `stripe_subscription_id` column on `organization_members` when needed.

```sql
-- Products / Merchandise (future)
CREATE TABLE products (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    category        VARCHAR(50),     -- 'equipment','apparel','accessories'
    price           DECIMAL(10,2) NOT NULL,
    currency        CHAR(3) NOT NULL,
    sku             VARCHAR(50),
    stock_quantity  INT DEFAULT 0,
    image_urls      JSONB DEFAULT '[]'::jsonb,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Group Training / Clinics (future)
CREATE TABLE training_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    court_id        UUID REFERENCES courts(id),
    instructor_id   UUID REFERENCES users(id),
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    session_type    VARCHAR(30) CHECK (session_type IN ('group_clinic','private_lesson','camp','drop_in')),
    max_participants INT NOT NULL,
    price_per_person DECIMAL(10,2) NOT NULL,
    currency        CHAR(3) NOT NULL,
    start_at        TIMESTAMPTZ NOT NULL,
    end_at          TIMESTAMPTZ NOT NULL,
    recurrence_rule JSONB,
    status          VARCHAR(20) DEFAULT 'scheduled',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Online Courses (future)
CREATE TABLE courses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      UUID REFERENCES organizations(id),   -- NULL = platform-level
    instructor_id   UUID REFERENCES users(id),
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    thumbnail_url   VARCHAR(500),
    price           DECIMAL(10,2),
    currency        CHAR(3) DEFAULT 'USD',
    is_free         BOOLEAN DEFAULT FALSE,
    status          VARCHAR(20) DEFAULT 'draft',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 4.3 Indexing Strategy Summary

| Access Pattern | Index | Type |
|----------------|-------|------|
| Double-booking prevention | `idx_no_double_booking` on `(court_id, start_at, end_at) WHERE active` | Unique partial |
| Availability grid (day view) | `idx_reservations_court_time` | Composite |
| User's upcoming bookings | `idx_reservations_user` on `(user_id, status)` | Composite |
| Organization day view | `idx_reservations_org_date` on `(org_id, local_date)` | Composite |
| Promo code lookup | `idx_discounts_code` on `(org_id, code) WHERE active` | Partial |
| Expired holds cleanup | `idx_reservations_status` on `(status, hold_expires_at) WHERE held` | Partial |
| Geo-based organization search | `idx_organizations_geo` on `(lat, lng)` | Composite (upgrade to PostGIS for radius queries) |

---

## 5. Authentication and Authorization

### 5.1 Auth Flow

```
User Login/Register
        â”‚
        â–¼
  POST /api/auth/login   (email+password, phone+OTP, or social OAuth)
        â”‚
        â–¼
  Server validates credentials
        â”‚
        â–¼
  Issue: Access Token (JWT, 15min) + Refresh Token (opaque, 30 days)
        â”‚
        â–¼
  Access Token Claims:
  {
    sub: "user-uuid",
    email: "user@example.com",
    platform_admin: true,                       // optional, omitted if false
    orgs: {
      "org-uuid-1": { "role": "owner",  "tier": null },
      "org-uuid-2": { "role": "member", "tier": "premium" },
      "org-uuid-3": { "role": "admin",  "tier": "free" }
    },
    iat, exp
  }
```

### 5.2 Role Hierarchy

| Role | Scope | Permissions |
|------|-------|-------------|
| **platform_admin** | Global | All operations; impersonate any organization; manage organizations |
| **owner** | Organization | Full organization management; billing; delete organization |
| **admin** | Organization | Manage courts, schedules, pricing, staff, bookings, reports |
| **manager** | Organization | Manage bookings, courts, schedules (no pricing/payment config) |
| **staff** | Organization | View/manage bookings; check-in users; limited actions |
| **member** | Organization | Book courts; view own reservations; manage own profile |

Roles and tiers are orthogonal. A user's **role** determines their permissions (what they can do), while their **tier** (via `membership_tiers`) determines their benefits (discounts, booking priority, advance booking window). For example, a `staff` member can also hold a `Premium` tier to get member discounts when booking for themselves.

### 5.3 Authorization Middleware (FastAPI Dependency Pattern)

```python
from fastapi import Depends, HTTPException, status
from typing import List

# Role hierarchy: higher roles implicitly include lower ones
ROLE_HIERARCHY = {
    "owner": 5,
    "admin": 4,
    "manager": 3,
    "staff": 2,
    "member": 1,
}

class OrgRoleChecker:
    """FastAPI dependency that enforces role-based access per organization."""

    def __init__(self, min_role: str):
        self.min_level = ROLE_HIERARCHY[min_role]

    async def __call__(
        self,
        org_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.is_platform_admin:
            return current_user

        membership = current_user.orgs.get(str(org_id))
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this organization",
            )

        user_level = ROLE_HIERARCHY.get(membership["role"], 0)
        if user_level < self.min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this organization",
            )
        return current_user

# Usage in route:
# @router.post("/courts")
# async def create_court(
#     ...,
#     user: User = Depends(OrgRoleChecker("admin")),   # admin+ (admin, owner)
# ):
```

### 5.4 API Key Authentication (For Integrations)

Organizations may need API keys for POS integrations or third-party systems. A separate `api_keys` table stores hashed keys with scoped permissions and rate limits.

---

## 6. API Endpoint Design

All endpoints are prefixed with `/api/v1`. Tenant-scoped endpoints include `orgId` either in the path or resolved from the subdomain/domain header.

### 6.1 Authentication

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/auth/register` | Register new user | Public |
| POST | `/auth/login` | Email/password or phone/OTP login | Public |
| POST | `/auth/login/social` | OAuth social login (Google, Apple, WeChat) | Public |
| POST | `/auth/refresh` | Refresh access token | Refresh Token |
| POST | `/auth/logout` | Revoke refresh token | Authenticated |
| POST | `/auth/forgot-password` | Send reset email/SMS | Public |
| POST | `/auth/reset-password` | Reset with token | Public |
| POST | `/auth/verify-email` | Email verification | Public (token) |
| POST | `/auth/verify-phone` | Phone OTP verification | Public (token) |

### 6.2 Users (Self-service)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/users/me` | Get current user profile | Authenticated |
| PATCH | `/users/me` | Update profile | Authenticated |
| GET | `/users/me/reservations` | All reservations across organizations | Authenticated |
| GET | `/users/me/organizations` | Organizations user is a member of | Authenticated |
| DELETE | `/users/me` | Soft-delete account | Authenticated |

### 6.3 Organizations (Public Discovery)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/organizations` | List/search organizations (public) | Public |
| GET | `/organizations/:orgId` | Organization detail + theme + hours | Public |
| GET | `/organizations/:orgId/courts` | List courts with status | Public |
| GET | `/organizations/:orgId/availability` | Availability grid for date range | Public |
| GET | `/organizations/by-domain/:domain` | Resolve organization from domain | Public |

**Availability endpoint detail:**

```
GET /organizations/:orgId/availability?date=2026-03-14&days=1&court_id=optional
```

Response: time-slot grid showing each court's availability and price per slot.

```json
{
  "org_id": "uuid",
  "date": "2026-03-14",
  "timezone": "Asia/Shanghai",
  "slot_interval_mins": 30,
  "courts": [
    {
      "court_id": "uuid",
      "name": "Court 1",
      "surface_type": "hard",
      "slots": [
        {
          "start_time": "09:00",
          "end_time": "09:30",
          "status": "available",
          "price": 150.00,
          "tier": "peak"
        },
        {
          "start_time": "09:30",
          "end_time": "10:00",
          "status": "booked",
          "price": 150.00,
          "tier": "peak"
        },
        {
          "start_time": "10:00",
          "end_time": "10:30",
          "status": "blocked",
          "reason": "maintenance",
          "price": null
        }
      ]
    }
  ]
}
```

### 6.4 Reservations (User-facing)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/organizations/:orgId/reservations` | Create reservation (hold slots) | Member+ |
| GET | `/organizations/:orgId/reservations/:id` | Get reservation detail | Owner/Staff+ |
| POST | `/organizations/:orgId/reservations/:id/confirm` | Confirm after payment | Member+ |
| POST | `/organizations/:orgId/reservations/:id/cancel` | Cancel reservation | Member+ |
| POST | `/organizations/:orgId/reservations/recurring` | Create recurring reservation series | Member+ |

**Create reservation request:**

```json
{
  "court_id": "uuid",
  "date": "2026-03-14",
  "start_time": "09:00",
  "end_time": "10:30",
  "player_count": 2,
  "discount_code": "SPRING20",
  "notes": "Will bring own balls"
}
```

### 6.5 Payments

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/organizations/:orgId/reservations/:id/payment-intent` | Create Stripe PaymentIntent | Member+ |
| POST | `/webhooks/stripe` | Stripe webhook receiver | Stripe signature |
| GET | `/organizations/:orgId/payments` | Payment history (admin) | Admin+ |
| POST | `/organizations/:orgId/payments/:id/refund` | Issue refund | Admin+ |

### 6.6 Discounts

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/organizations/:orgId/discounts/validate` | Validate a promo code | Member+ |
| GET | `/organizations/:orgId/discounts` | List all discounts | Staff+ |
| POST | `/organizations/:orgId/discounts` | Create discount | Admin+ |
| PATCH | `/organizations/:orgId/discounts/:id` | Update discount | Admin+ |
| DELETE | `/organizations/:orgId/discounts/:id` | Deactivate discount | Admin+ |

### 6.7 Organization Admin -- Courts

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/admin/organizations/:orgId/courts` | Create court | Admin+ |
| PATCH | `/admin/organizations/:orgId/courts/:id` | Update court | Admin+ |
| DELETE | `/admin/organizations/:orgId/courts/:id` | Deactivate court | Admin+ |
| POST | `/admin/organizations/:orgId/courts/:id/blocks` | Create maintenance block | Staff+ |
| DELETE | `/admin/organizations/:orgId/court-blocks/:id` | Remove block | Staff+ |

### 6.8 Organization Admin -- Schedules

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/admin/organizations/:orgId/schedules` | List operating schedules | Staff+ |
| POST | `/admin/organizations/:orgId/schedules` | Create schedule rule | Admin+ |
| PATCH | `/admin/organizations/:orgId/schedules/:id` | Update schedule | Admin+ |
| DELETE | `/admin/organizations/:orgId/schedules/:id` | Delete schedule | Admin+ |

### 6.9 Organization Admin -- Pricing

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/admin/organizations/:orgId/pricing-rules` | List pricing rules | Staff+ |
| POST | `/admin/organizations/:orgId/pricing-rules` | Create pricing rule | Admin+ |
| PATCH | `/admin/organizations/:orgId/pricing-rules/:id` | Update rule | Admin+ |
| DELETE | `/admin/organizations/:orgId/pricing-rules/:id` | Delete rule | Admin+ |
| GET | `/admin/organizations/:orgId/pricing/preview` | Preview pricing for date/court | Admin+ |

### 6.10 Organization Admin -- Staff and Members

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/admin/organizations/:orgId/members` | List members with roles | Staff+ |
| POST | `/admin/organizations/:orgId/members/invite` | Invite staff/admin by email | Admin+ |
| PATCH | `/admin/organizations/:orgId/members/:userId` | Update role | Owner+ |
| DELETE | `/admin/organizations/:orgId/members/:userId` | Remove member | Admin+ |

### 6.11 Organization Admin -- Settings and Theming

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/admin/organizations/:orgId/settings` | Get organization settings | Admin+ |
| PATCH | `/admin/organizations/:orgId/settings` | Update settings | Admin+ |
| GET | `/admin/organizations/:orgId/theme` | Get theme | Admin+ |
| PUT | `/admin/organizations/:orgId/theme` | Set/update theme | Admin+ |
| POST | `/admin/organizations/:orgId/logo` | Upload logo | Admin+ |

### 6.12 Organization Admin -- Reports and Dashboard

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/admin/organizations/:orgId/dashboard` | Summary stats (today's bookings, revenue, utilization) | Staff+ |
| GET | `/admin/organizations/:orgId/reports/revenue` | Revenue report with filters | Admin+ |
| GET | `/admin/organizations/:orgId/reports/utilization` | Court utilization report | Admin+ |
| GET | `/admin/organizations/:orgId/reports/bookings` | Booking report | Admin+ |

### 6.13 Platform Admin

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/platform/organizations` | List all organizations | Platform Admin |
| POST | `/platform/organizations` | Create/onboard organization | Platform Admin |
| PATCH | `/platform/organizations/:id` | Update organization status | Platform Admin |
| GET | `/platform/users` | List all users | Platform Admin |
| GET | `/platform/reports/revenue` | Platform-wide revenue | Platform Admin |
| GET | `/platform/reports/growth` | Growth metrics | Platform Admin |

---

## 7. Reservation and Booking Engine

### 7.1 Booking Flow (State Machine)

```
  User selects slots
        â”‚
        â–¼
  [HELD] â”€â”€â”€â”€ hold_expires_at (5 min TTL)
        â”‚                    â”‚
   Payment initiated    Timer expires
        â”‚                    â”‚
        â–¼                    â–¼
  [PENDING_PAYMENT]    [released / deleted]
        â”‚
   Stripe webhook: payment_intent.succeeded
        â”‚
        â–¼
  [CONFIRMED]
        â”‚
        â”œâ”€â”€ User checks in â”€â”€â–¶ [CHECKED_IN] â”€â”€â–¶ [COMPLETED]
        â”‚
        â”œâ”€â”€ User cancels â”€â”€â–¶ [CANCELLED] â”€â”€â–¶ refund logic
        â”‚
        â”œâ”€â”€ Admin cancels â”€â”€â–¶ [ADMIN_CANCELLED] â”€â”€â–¶ full refund
        â”‚
        â””â”€â”€ No-show â”€â”€â–¶ [NO_SHOW]
```

### 7.2 Double-Booking Prevention (Critical Path)

The system uses a three-layer defense:

**Layer 1 -- Application-level optimistic check:**
Before attempting to create a reservation, query existing active reservations for the court and time range.

**Layer 2 -- Database-level exclusive row lock:**
```sql
-- Within a SERIALIZABLE or explicit advisory lock transaction:
SELECT id FROM reservations
WHERE court_id = $1
  AND status NOT IN ('cancelled','admin_cancelled','refunded')
  AND start_at < $3   -- requested end
  AND end_at > $2     -- requested start
FOR UPDATE NOWAIT;     -- fail immediately if locked
```

**Layer 3 -- Database constraint (ultimate safety net):**
The exclusion constraint or unique partial index described in section 4.2.11 ensures that even under race conditions, the database itself rejects conflicting inserts.

### 7.3 Hold-and-Release Pattern

When a user selects time slots:
1. Insert reservation with `status = 'held'` and `hold_expires_at = now() + 5 minutes`.
2. A BullMQ delayed job fires at `hold_expires_at` to check status; if still `held`, delete the reservation and release the slot.
3. Redis key `hold:{court_id}:{slot_start}` provides fast availability checks during the hold window without hitting the database.

### 7.4 Recurring Reservations

```json
POST /organizations/:orgId/reservations/recurring
{
  "court_id": "uuid",
  "start_time": "09:00",
  "end_time": "10:00",
  "recurrence": {
    "frequency": "weekly",
    "day_of_week": 3,
    "start_date": "2026-03-18",
    "end_date": "2026-06-03",
    "exceptions": ["2026-04-15"]
  }
}
```

Processing:
1. Generate all individual reservation dates from the recurrence rule.
2. Check availability for each date.
3. Return a preview showing which dates are available and which conflict.
4. User confirms; all available dates are booked as individual `reservation` rows sharing a `recurrence_group_id`.
5. Each reservation is paid individually (or as a batch via a single Stripe PaymentIntent with the total).

---

## 8. Payment Flow

### 8.1 Multi-Provider Architecture

The payment system is provider-agnostic. Each organization connects one or more payment accounts (Stripe, WeChat Pay, Alipay, etc.) via the `payment_accounts` table. The platform routes payments to the appropriate provider based on the organization's configuration and the user's chosen payment method.

```
                     +------------------+
                     |    RallyAI       |
                     |    Platform      |
                     +--------+---------+
                              |
              +---------------+---------------+
              |               |               |
       +------v------+ +-----v-------+ +-----v-------+
       |   Stripe    | | WeChat Pay  | |   Alipay    |
       |   Gateway   | |   Gateway   | |   Gateway   |
       +------+------+ +-----+-------+ +-----+-------+
              |               |               |
        +-----v-----+  +-----v-----+   +-----v-----+
        | Org A      |  | Org B     |   | Org C     |
        | (Stripe    |  | (WeChat   |   | (Alipay   |
        |  Express)  |  |  Merchant)|   |  + Stripe)|
        +------------+  +-----------+   +-----------+
```

An organization can have multiple payment accounts (e.g., Stripe for international cards + WeChat Pay for Chinese users). The frontend displays available payment methods based on the organization's connected accounts.

### 8.2 Payment Sequence

```
1. User confirms reservation
   |
2. Frontend calls: POST /organizations/:orgId/reservations/:id/checkout
   |
3. Backend resolves payment provider:
   |   a. Look up org's active payment_accounts
   |   b. Match against user's chosen payment method
   |   c. Delegate to provider-specific adapter:
   |      - Stripe: create PaymentIntent with application_fee + transfer
   |      - WeChat Pay: create unified order via JSAPI/Native
   |      - Alipay: create trade via alipay.trade.create
   |
4. Return provider-specific client payload (client_secret, prepay_id, etc.)
   |
5. Frontend completes payment via provider SDK
   |
6. Provider sends async notification (webhook / callback)
   |
7. Backend webhook handler (per-provider):
   |   a. Verify signature (Stripe sig, WeChat sign, Alipay sign)
   |   b. Update payment.status = 'succeeded'
   |   c. Update reservation.status = 'confirmed'
   |   d. Send confirmation notification
   |   e. Emit 'reservation.confirmed' event
```

### 8.3 Refund Logic

```
Cancellation request received
        |
        v
  Resolve cancellation policy (court-level, or org default)
        |
        v
  Is cancellation > N hours before start_at?
        |                       |
       YES                      NO
        |                       |
  Full refund              Apply cancellation_fee_percent
        |                       |
        v                       v
  Provider refund API      Provider refund API
  (full amount)            (partial amount)
        |                       |
        v                       v
  payment.status =         payment.status =
  'refunded'               'partially_refunded'
```

Refund amounts are calculated as:
- `refund_amount = total_amount` if outside cancellation window
- `refund_amount = total_amount * (1 - cancellation_fee_percent / 100)` if inside window

The cancellation policy is resolved from the court first (`courts.cancellation_policy_hours`), falling back to the organization default (`organizations.cancellation_policy_hours`).

---

## 9. Pricing and Discount Engine

### 9.1 Price Resolution Algorithm

For a given `(court_id, date, time_slot)`:

```
1. Get all active pricing_rules where:
   a. court_id matches this court (or rule.court_id IS NULL for org-wide fallback)
   b. day_of_week includes this date's day (or NULL for all days)
   c. slot start_time falls within rule's [start_time, end_time) (or NULL for all times)
   d. date falls within [valid_from, valid_until] (or NULL for always valid)
2. Sort matching rules by priority DESC
3. First match wins -> return price_per_slot, list_price_per_slot, and tier
4. If no rule matches -> fall back to courts.base_price_per_slot
5. If neither exists -> slot is not bookable (configuration error)
6. Apply member tier discount: final_price = price * (1 - member.discount_percent / 100)
7. For display: show list_price_per_slot as strikethrough if it differs from final price
```

**Example: Configuring time-of-day pricing (from reference apps)**

| Rule | Court | Days | Time Band | Price | List Price | Priority |
|------|-------|------|-----------|-------|------------|----------|
| Morning Off-Peak | Court 01 | Mon-Sun | 07:00-10:00 | ¥118 | ¥108 | 10 |
| Daytime Peak | Court 01 | Mon-Sun | 10:00-22:00 | ¥148 | ¥208 | 10 |
| Morning Off-Peak | Court 02 | Mon-Sun | 07:00-10:00 | ¥98 | NULL | 10 |
| Daytime Peak | Court 02 | Mon-Sun | 10:00-22:00 | ¥128 | ¥188 | 10 |

### 9.2 Discount Application

```
1. User submits discount_code at checkout
2. Validate:
   a. Code exists and is_active for this organization
   b. valid_from <= now <= valid_until
   c. current_uses < max_uses_total
   d. User hasn't exceeded max_uses_per_user
   e. Booking meets min_booking_amount
   f. Court and day/time restrictions match
3. Calculate discount:
   a. percentage â†’ subtotal * (discount_value / 100), capped at max_discount_amount
   b. fixed_amount â†’ min(discount_value, subtotal)
4. Return: { subtotal, discount_amount, tax_amount, total }
5. On booking confirmation: increment current_uses atomically
```

---

## 10. Time Zone Handling

This is a critical concern given the screenshots show facilities in China (Asia/Shanghai).

### 10.1 Rules

1. **Database stores all timestamps in UTC** (`TIMESTAMPTZ`).
2. Each organization has a `timezone` field (IANA format, e.g., `Asia/Shanghai`).
3. **Operating schedules and pricing rules use local `TIME`** values (no timezone) -- they represent wall-clock time at the facility.
4. **Reservations store both UTC (`start_at`, `end_at`) and denormalized local (`local_date`, `local_start_time`, `local_end_time`)** for efficient querying.
5. The API accepts and returns local times for user-facing endpoints, converting to/from UTC on the server using the organization's timezone.
6. The availability grid is always rendered in the organization's local timezone.
7. **DST handling**: For organizations in timezones with DST transitions, recurring reservations must be recomputed across DST boundaries to maintain the same wall-clock time.

### 10.2 Conversion Example

```python
from zoneinfo import ZoneInfo
from datetime import datetime

# User books Court 1 at "09:00" on "2026-03-14" for organization in Asia/Shanghai
org_tz = ZoneInfo("Asia/Shanghai")
local_start = datetime(2026, 3, 14, 9, 0, tzinfo=org_tz)
utc_start = local_start.astimezone(ZoneInfo("UTC"))
# → 2026-03-14T01:00:00+00:00  (UTC)
```

---

## 11. Extensibility Design

The schema and API are designed for future growth through these patterns:

### 11.1 Polymorphic Order/Payment System

When merchandise and training sessions are added, the `payments` table will reference an `order` table rather than directly referencing `reservations`. Preparation for this:

- The `payments.metadata` JSONB field can carry `order_type` and `order_id` for early prototyping.
- A future `orders` table will act as a polymorphic parent: `order_type IN ('court_reservation', 'merchandise', 'training_session', 'course_purchase', 'membership')`.
- `reservations` becomes one type of "line item" in the order.

### 11.2 Feature Flags Per Organization

```sql
CREATE TABLE organization_features (
    org_id  UUID REFERENCES organizations(id),
    feature     VARCHAR(50) NOT NULL,  -- 'merchandise', 'group_training', 'courses', 'memberships'
    enabled     BOOLEAN DEFAULT FALSE,
    config      JSONB DEFAULT '{}'::jsonb,
    PRIMARY KEY (org_id, feature)
);
```

This allows gradual rollout of new features per organization.

### 11.3 Module Registration Pattern (Code)

```python
# FastAPI router-based module pattern
from fastapi import APIRouter, FastAPI

def create_merchandise_router() -> APIRouter:
    """Self-contained feature module with its own routes and dependencies."""
    router = APIRouter(prefix="/merchandise", tags=["merchandise"])

    @router.get("/products")
    async def list_products(...):
        ...

    @router.post("/orders")
    async def create_order(...):
        ...

    return router

# In main app setup, conditionally include based on feature flags:
def register_modules(app: FastAPI, enabled_features: set[str]):
    if "merchandise" in enabled_features:
        app.include_router(create_merchandise_router())
    if "group_training" in enabled_features:
        app.include_router(create_training_router())
```

Each future feature is a self-contained router module that plugs into the existing organization and payment infrastructure.

---

## 12. Performance and Scaling Considerations

### 12.1 Caching Strategy

| Data | Cache Location | TTL | Invalidation |
|------|---------------|-----|-------------|
| Organization details + theme | Redis + CDN | 5 min | On update (pub/sub) |
| Court list per organization | Redis | 2 min | On court CRUD |
| Availability grid | Redis | 30 sec | On booking/cancellation |
| Pricing rules | Redis | 5 min | On rule change |
| User session/JWT | Stateless (JWT) | 15 min | Token expiry |

### 12.2 Availability Query Optimization

The availability grid is the highest-traffic read query. Optimization path:

1. **Cache the grid** per organization per date in Redis with 30-second TTL.
2. On any booking or cancellation, invalidate that date's cache for the affected organization.
3. Pre-compute next-day availability during off-peak hours.
4. For the grid query itself, a single SQL query joins `courts`, `operating_schedules`, `reservations`, `court_blocks`, and `pricing_rules` for the requested date.

### 12.3 Connection Pooling

Use **SQLAlchemy's async connection pool** (`create_async_engine(pool_size=20, max_overflow=10)`) or **PgBouncer** in front of PostgreSQL. With horizontal scaling to 4 uvicorn instances, that is 80-120 connections -- well within PostgreSQL's comfort zone.

### 12.4 Horizontal Scaling Path

```
10K users â†’ Single API instance + PostgreSQL + Redis
50K users â†’ 2-3 API instances behind LB; read replicas for reports
200K users â†’ Dedicated read replica for availability queries; 
             Redis Cluster; consider CQRS for reporting
1M+ users  â†’ Evaluate database-per-region sharding; 
             CDN-cached availability with WebSocket updates
```

### 12.5 Background Jobs (Celery / ARQ)

| Job | Trigger | Description |
|-----|---------|-------------|
| `expire_held_slots` | Delayed (5 min) | Release expired reservation holds |
| `send_confirmation` | On booking confirmed | Email/SMS/push notification |
| `send_reminder` | Scheduled (2h before) | Booking reminder |
| `process_no_shows` | Scheduled (30 min after slot end) | Mark no-shows |
| `generate_recurring` | On recurring booking request | Create all instances |
| `daily_reports` | Celery Beat cron (organization timezone aware) | Generate daily revenue/utilization |
| `cleanup_expired_tokens` | Celery Beat cron (daily) | Purge expired refresh tokens |

---

## 13. Edge Cases and Failure Modes

### 13.1 Double-Booking Race Condition
**Scenario**: Two users click "book" for the same slot at the same instant.
**Solution**: The `FOR UPDATE NOWAIT` lock in the transaction causes the second request to fail immediately. The database exclusion constraint is the ultimate safety net. The API returns `409 Conflict` with a message suggesting the user refresh availability.

### 13.2 Payment Succeeds but Webhook Fails
**Scenario**: Stripe charges the user, but the webhook delivery fails.
**Solution**: The reservation stays in `pending_payment`. A reconciliation job runs every 5 minutes, querying Stripe for PaymentIntents matching pending reservations, and confirms any that succeeded. Stripe also retries webhooks for up to 3 days.

### 13.3 User Closes Browser During Payment
**Scenario**: PaymentIntent created, user navigates away.
**Solution**: The reservation is in `held` status with a 5-minute expiry. If payment completes (via Stripe webhook), it transitions to `confirmed`. If not, the hold-expiry job releases the slot. If the user's payment actually went through but the hold expired, the reconciliation job catches it and restores the reservation.

### 13.4 Timezone DST Transition for Recurring Bookings
**Scenario**: Weekly booking at 9 AM, but DST "spring forward" causes a gap.
**Solution**: Recurring instances are generated using wall-clock time in the organization timezone, not by adding 7*24 hours. Python's `zoneinfo` + `datetime` handles this correctly. Each instance is independently converted to UTC.

### 13.5 Organization Changes Pricing After User Holds Slot
**Scenario**: Admin updates pricing while a user has a held reservation.
**Solution**: The price is locked at hold time via `pricing_snapshot` in the reservation. The user pays the price they were shown. The snapshot serves as an immutable record.

### 13.6 Court Taken Offline During Active Bookings
**Scenario**: Admin marks a court as "maintenance" but there are future confirmed bookings.
**Solution**: The API returns a list of affected reservations and requires explicit confirmation. Admin must choose: (a) cancel and refund affected bookings, or (b) block only unbooked future slots.

### 13.7 Concurrent Discount Redemption
**Scenario**: A promo code has 1 use left; two users try to apply it simultaneously.
**Solution**: `current_uses` is incremented atomically: `UPDATE discounts SET current_uses = current_uses + 1 WHERE id = $1 AND current_uses < max_uses_total RETURNING id`. If no row is returned, the discount is exhausted.

---

## Appendix A: Environment Variables

```
# Database
DATABASE_URL=postgresql://user:pass@host:5432/rallyai
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://host:6379

# Auth
JWT_SECRET=<random-256-bit>
JWT_EXPIRY=900
REFRESH_TOKEN_EXPIRY=2592000

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PLATFORM_ACCOUNT=acct_...

# Storage
S3_BUCKET=rallyai-assets
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# App
APP_URL=https://rallyai.com
API_URL=https://api.rallyai.com
APP_ENV=production
LOG_LEVEL=info

# Celery
CELERY_BROKER_URL=redis://host:6379/1
```

---

## Appendix B: Directory Structure (Proposed)

```
rallyai/
├── backend/                          # FastAPI Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entrypoint
│   │   ├── config.py                 # Pydantic Settings (env vars)
│   │   ├── database.py               # SQLAlchemy engine, session factory
│   │   │
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── court.py
│   │   │   ├── schedule.py
│   │   │   ├── pricing.py
│   │   │   ├── reservation.py
│   │   │   ├── payment.py
│   │   │   ├── discount.py
│   │   │   └── audit.py
│   │   │
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── court.py
│   │   │   ├── reservation.py
│   │   │   ├── payment.py
│   │   │   └── common.py             # Pagination, error responses
│   │   │
│   │   ├── api/                      # Route handlers (routers)
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── organizations.py
│   │   │   │   ├── courts.py
│   │   │   │   ├── schedules.py
│   │   │   │   ├── pricing.py
│   │   │   │   ├── reservations.py
│   │   │   │   ├── payments.py
│   │   │   │   ├── discounts.py
│   │   │   │   ├── admin.py          # Organization admin endpoints
│   │   │   │   └── platform.py       # Platform super-admin
│   │   │   └── deps.py               # Shared dependencies (get_db, get_current_user)
│   │   │
│   │   ├── services/                 # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── booking.py            # Core booking engine
│   │   │   ├── pricing.py            # Price resolution engine
│   │   │   ├── payment.py            # Stripe integration
│   │   │   ├── availability.py       # Availability grid computation
│   │   │   └── notification.py       # Email, SMS, push
│   │   │
│   │   ├── core/                     # Cross-cutting concerns
│   │   │   ├── __init__.py
│   │   │   ├── security.py           # JWT creation/verification, password hashing
│   │   │   ├── permissions.py        # TenantRoleChecker, role decorators
│   │   │   ├── exceptions.py         # Custom exception handlers
│   │   │   └── middleware.py         # Tenant context, request logging
│   │   │
│   │   └── tasks/                    # Celery / ARQ background tasks
│   │       ├── __init__.py
│   │       ├── celery_app.py         # Celery configuration
│   │       ├── booking_tasks.py      # expire_held_slots, process_no_shows
│   │       ├── notification_tasks.py # send_confirmation, send_reminder
│   │       └── report_tasks.py       # daily_reports
│   │
│   ├── alembic/                      # Database migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── alembic.ini
│   ├── seeds/                        # Seed data scripts
│   │   └── seed_dev.py
│   ├── tests/
│   │   ├── conftest.py               # Fixtures (test DB, client, auth)
│   │   ├── test_auth.py
│   │   ├── test_booking.py
│   │   ├── test_pricing.py
│   │   └── test_payments.py
│   ├── pyproject.toml                # Dependencies (uv / poetry)
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                         # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── (public)/             # User-facing: booking, courts
│   │   │   ├── (admin)/              # Organization admin dashboard
│   │   │   └── (platform)/           # Platform super-admin
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   │   └── api-client.ts         # Auto-generated from OpenAPI spec
│   │   └── styles/
│   └── package.json
│
├── docker-compose.yml                # PostgreSQL, Redis, backend, frontend
├── Makefile                          # Common dev commands
└── README.md
```

---

This concludes the design document. The schema covers all requested entities with room for growth. The API design is RESTful, role-aware, and organized by domain. The booking engine addresses double-booking, holds, recurring reservations, and timezone correctness. The payment flow uses Stripe Connect for proper multi-tenant fund splitting. The extensibility tables and router module patterns ensure that merchandise, training, courses, and memberships can be added without rearchitecting.

---

### Critical Files for Implementation

These are the files that should be created first, in priority order, when beginning implementation:

- **`backend/app/models/*.py`** + **`alembic/`** - SQLAlchemy ORM models translating all SQL table definitions above, plus Alembic migration setup. Every other module depends on the models being correct and complete.
- **`backend/app/services/booking.py`** - Core booking engine containing the hold-and-release pattern, double-booking prevention logic, availability grid computation, and recurring reservation generation. This is the most complex business logic in the system.
- **`backend/app/core/security.py`** + **`backend/app/core/permissions.py`** - Multi-tenant JWT authentication with role resolution per organization. Every protected endpoint depends on these modules.
- **`backend/app/services/pricing.py`** - The pricing rule evaluation engine that resolves the correct price for any (court, date, time) tuple by evaluating rules in priority order. Used by both the availability grid and the checkout flow.
- **`backend/app/services/payment.py`** - Stripe Connect integration handling PaymentIntent creation, webhook processing, refund logic, and the payment reconciliation task. Ties the booking engine to real money movement.

---

### Appendix C: Key Python Dependencies

```toml
# pyproject.toml [project.dependencies]
fastapi = ">=0.115"
uvicorn = {extras = ["standard"], version = ">=0.34"}
sqlalchemy = {extras = ["asyncio"], version = ">=2.0"}
asyncpg = ">=0.30"              # Async PostgreSQL driver
alembic = ">=1.14"
pydantic = ">=2.10"
pydantic-settings = ">=2.7"
python-jose = {extras = ["cryptography"], version = ">=3.3"}
passlib = {extras = ["bcrypt"], version = ">=1.7"}
stripe = ">=12.0"
redis = {extras = ["hiredis"], version = ">=5.0"}
celery = {extras = ["redis"], version = ">=5.4"}
boto3 = ">=1.35"
httpx = ">=0.28"                # Async HTTP client
python-multipart = ">=0.0.18"   # File uploads
emails = ">=0.6"                # Email sending

# Dev dependencies
pytest = ">=8.0"
pytest-asyncio = ">=0.24"
httpx = ">=0.28"                # TestClient
factory-boy = ">=3.3"           # Test factories
ruff = ">=0.8"                  # Linting + formatting
mypy = ">=1.13"                 # Type checking
```