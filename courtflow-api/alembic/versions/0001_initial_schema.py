"""Initial schema with membership tiers, user memberships, and court metadata.

Revision ID: 0001
Revises:
Create Date: 2026-03-17
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # organizations
    # ------------------------------------------------------------------
    op.create_table(
        "organizations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("slug", sa.String(64), unique=True, nullable=False),
        sa.Column("logo_url", sa.Text, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_partner", sa.Boolean, default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("wechat_openid", sa.String(128), unique=True, nullable=True),
        sa.Column("wechat_unionid", sa.String(128), unique=True, nullable=True),
        sa.Column("phone", sa.String(20), unique=True, nullable=True),
        sa.Column("nickname", sa.String(64), nullable=True),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("bio", sa.String(200), nullable=True),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("birthday", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email", sa.String(254), unique=True, nullable=True),
        sa.Column(
            "player_level",
            sa.Enum(
                "beginner",
                "elementary",
                "intermediate",
                "advanced",
                "professional",
                name="playerlevel",
            ),
            nullable=False,
            server_default="beginner",
        ),
        sa.Column(
            "dominant_hand",
            sa.Enum("left", "right", name="dominanthand"),
            nullable=True,
        ),
        sa.Column(
            "backhand_type",
            sa.Enum("two_handed", "one_handed", name="backhandtype"),
            nullable=True,
        ),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("token_hash", sa.String(128), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean, default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ------------------------------------------------------------------
    # venues
    # ------------------------------------------------------------------
    op.create_table(
        "venues",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("address", sa.String(300), nullable=False),
        sa.Column("city", sa.String(64), nullable=False),
        sa.Column("district", sa.String(64), nullable=True),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=True),
        sa.Column(
            "timezone", sa.String(64), server_default="Asia/Shanghai", nullable=False
        ),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("wechat_cs", sa.String(200), nullable=True),
        sa.Column("parking_info", sa.String(300), nullable=True),
        sa.Column("open_time", sa.String(5), server_default="08:00", nullable=False),
        sa.Column("close_time", sa.String(5), server_default="22:00", nullable=False),
        sa.Column(
            "slot_duration_minutes", sa.Integer, server_default="60", nullable=False
        ),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "venue_media",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "venue_id", UUID(as_uuid=True), sa.ForeignKey("venues.id"), nullable=False
        ),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("media_type", sa.String(20), nullable=False),
        sa.Column("sort_order", sa.Integer, default=0, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "venue_facilities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "venue_id", UUID(as_uuid=True), sa.ForeignKey("venues.id"), nullable=False
        ),
        sa.Column("key", sa.String(64), nullable=False),
        sa.Column("label", sa.String(64), nullable=False),
        sa.Column("icon", sa.String(64), nullable=True),
        sa.Column("description", sa.String(200), nullable=True),
    )

    # ------------------------------------------------------------------
    # courts
    # ------------------------------------------------------------------
    op.create_table(
        "court_types",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "venue_id", UUID(as_uuid=True), sa.ForeignKey("venues.id"), nullable=False
        ),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("description", sa.String(200), nullable=True),
        sa.Column("icon", sa.String(64), nullable=True),
        sa.Column("sort_order", sa.Integer, default=0, nullable=False),
    )

    op.create_table(
        "courts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "venue_id", UUID(as_uuid=True), sa.ForeignKey("venues.id"), nullable=False
        ),
        sa.Column(
            "court_type_id",
            UUID(as_uuid=True),
            sa.ForeignKey("court_types.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("surface", sa.String(32), nullable=True),
        sa.Column("is_indoor", sa.Boolean, default=True, nullable=False),
        sa.Column("sort_order", sa.Integer, default=0, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "court_blocks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "court_id", UUID(as_uuid=True), sa.ForeignKey("courts.id"), nullable=False
        ),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(200), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "court_links",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "court_id", UUID(as_uuid=True), sa.ForeignKey("courts.id"), nullable=False
        ),
        sa.Column(
            "linked_court_id",
            UUID(as_uuid=True),
            sa.ForeignKey("courts.id"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
    )

    # ------------------------------------------------------------------
    # membership tiers (org-scoped, venue-scoped, court-type-scoped, court-scoped)
    # ------------------------------------------------------------------
    op.create_table(
        "membership_tiers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "scope",
            sa.Enum(
                "organization",
                "venue",
                "court_type",
                "court",
                name="membershiptierscope",
            ),
            nullable=False,
            server_default="organization",
        ),
        sa.Column(
            "venue_id", UUID(as_uuid=True), sa.ForeignKey("venues.id"), nullable=True
        ),
        sa.Column(
            "court_type_id",
            UUID(as_uuid=True),
            sa.ForeignKey("court_types.id"),
            nullable=True,
        ),
        sa.Column(
            "court_id", UUID(as_uuid=True), sa.ForeignKey("courts.id"), nullable=True
        ),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("description", sa.String(300), nullable=True),
        sa.Column("priority", sa.Integer, default=0, nullable=False),
        sa.Column("price_cents", sa.Integer, default=0, nullable=False),
        sa.Column("duration_days", sa.Integer, default=30, nullable=False),
        sa.Column("price_discount_pct", sa.Integer, default=0, nullable=False),
        sa.Column("booking_window_days", sa.Integer, default=7, nullable=False),
        sa.Column("monthly_hour_quota", sa.Integer, nullable=True),
        sa.Column("max_concurrent_bookings", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ------------------------------------------------------------------
    # organization members
    # ------------------------------------------------------------------
    op.create_table(
        "organization_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "tier_id",
            UUID(as_uuid=True),
            sa.ForeignKey("membership_tiers.id"),
            nullable=True,
        ),
        sa.Column(
            "role",
            sa.Enum("owner", "admin", "staff", "coach", "member", name="orgmemberrole"),
            nullable=False,
            server_default="member",
        ),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ------------------------------------------------------------------
    # schedules
    # ------------------------------------------------------------------
    op.create_table(
        "operating_schedules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "venue_id", UUID(as_uuid=True), sa.ForeignKey("venues.id"), nullable=False
        ),
        sa.Column("weekday", sa.Integer, nullable=True),
        sa.Column("override_date", sa.Date, nullable=True),
        sa.Column("open_time", sa.String(5), nullable=True),
        sa.Column("close_time", sa.String(5), nullable=True),
        sa.Column("is_closed", sa.Boolean, default=False, nullable=False),
        sa.Column("note", sa.String(200), nullable=True),
    )

    # ------------------------------------------------------------------
    # pricing rules
    # ------------------------------------------------------------------
    op.create_table(
        "pricing_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "venue_id", UUID(as_uuid=True), sa.ForeignKey("venues.id"), nullable=False
        ),
        sa.Column(
            "court_id", UUID(as_uuid=True), sa.ForeignKey("courts.id"), nullable=True
        ),
        sa.Column(
            "court_type_id",
            UUID(as_uuid=True),
            sa.ForeignKey("court_types.id"),
            nullable=True,
        ),
        sa.Column(
            "membership_tier_id",
            UUID(as_uuid=True),
            sa.ForeignKey("membership_tiers.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("priority", sa.Integer, default=0, nullable=False),
        sa.Column("weekdays", sa.String(13), nullable=True),
        sa.Column("date_from", sa.Date, nullable=True),
        sa.Column("date_to", sa.Date, nullable=True),
        sa.Column("time_from", sa.Time, nullable=True),
        sa.Column("time_to", sa.Time, nullable=True),
        sa.Column("is_holiday", sa.Boolean, nullable=True),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("original_amount_cents", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ------------------------------------------------------------------
    # discounts
    # ------------------------------------------------------------------
    op.create_table(
        "discounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "venue_id", UUID(as_uuid=True), sa.ForeignKey("venues.id"), nullable=True
        ),
        sa.Column("code", sa.String(32), unique=True, nullable=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column(
            "discount_type",
            sa.Enum("flat_off", "percent_off", "free_slot", name="discounttype"),
            nullable=False,
        ),
        sa.Column("value", sa.Integer, nullable=False),
        sa.Column("min_order_cents", sa.Integer, nullable=True),
        sa.Column("max_uses", sa.Integer, nullable=True),
        sa.Column("max_uses_per_user", sa.Integer, nullable=True),
        sa.Column("uses_count", sa.Integer, default=0, nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ------------------------------------------------------------------
    # orders
    # ------------------------------------------------------------------
    op.create_table(
        "orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "venue_id", UUID(as_uuid=True), sa.ForeignKey("venues.id"), nullable=False
        ),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("subtotal_cents", sa.Integer, nullable=False),
        sa.Column("discount_cents", sa.Integer, default=0, nullable=False),
        sa.Column("total_cents", sa.Integer, nullable=False),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "order_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "order_id", UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=False
        ),
        sa.Column("item_type", sa.String(20), nullable=False),
        sa.Column("item_id", UUID(as_uuid=True), nullable=False),
        sa.Column("description", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Integer, default=1, nullable=False),
        sa.Column("unit_price_cents", sa.Integer, nullable=False),
        sa.Column("total_cents", sa.Integer, nullable=False),
    )

    # ------------------------------------------------------------------
    # user memberships
    # ------------------------------------------------------------------
    op.create_table(
        "user_memberships",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "tier_id",
            UUID(as_uuid=True),
            sa.ForeignKey("membership_tiers.id"),
            nullable=False,
        ),
        sa.Column(
            "order_id", UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=True
        ),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "expired",
                "cancelled",
                "suspended",
                name="usermembershipstatus",
            ),
            nullable=False,
            server_default="active",
        ),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_user_memberships_user_status", "user_memberships", ["user_id", "status"]
    )

    # ------------------------------------------------------------------
    # reservations
    # ------------------------------------------------------------------
    op.create_table(
        "reservations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "court_id", UUID(as_uuid=True), sa.ForeignKey("courts.id"), nullable=False
        ),
        sa.Column(
            "order_id", UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=True
        ),
        sa.Column("slot_date", sa.Date, nullable=False),
        sa.Column("slot_start", sa.Time, nullable=False),
        sa.Column("slot_end", sa.Time, nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="held"),
        sa.Column("hold_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "court_id", "slot_date", "slot_start", name="uq_court_slot"
        ),
    )
    op.create_index(
        "ix_reservations_court_date", "reservations", ["court_id", "slot_date"]
    )

    # ------------------------------------------------------------------
    # payments
    # ------------------------------------------------------------------
    op.create_table(
        "payment_accounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "venue_id", UUID(as_uuid=True), sa.ForeignKey("venues.id"), nullable=False
        ),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("merchant_id", sa.String(128), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "payments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "order_id", UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=False
        ),
        sa.Column(
            "payment_account_id",
            UUID(as_uuid=True),
            sa.ForeignKey("payment_accounts.id"),
            nullable=True,
        ),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("provider_order_id", sa.String(128), unique=True, nullable=True),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ------------------------------------------------------------------
    # banners & audit
    # ------------------------------------------------------------------
    op.create_table(
        "banners",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=True,
        ),
        sa.Column(
            "venue_id", UUID(as_uuid=True), sa.ForeignKey("venues.id"), nullable=True
        ),
        sa.Column("image_url", sa.Text, nullable=False),
        sa.Column("link_url", sa.Text, nullable=True),
        sa.Column("title", sa.String(128), nullable=True),
        sa.Column("sort_order", sa.Integer, default=0, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_id", UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=True),
        sa.Column("resource_id", UUID(as_uuid=True), nullable=True),
        sa.Column("detail", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("banners")
    op.drop_table("payments")
    op.drop_table("payment_accounts")
    op.drop_index("ix_reservations_court_date", "reservations")
    op.drop_table("reservations")
    op.drop_index("ix_user_memberships_user_status", "user_memberships")
    op.drop_table("user_memberships")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("discounts")
    op.drop_table("pricing_rules")
    op.drop_table("operating_schedules")
    op.drop_table("organization_members")
    op.drop_table("membership_tiers")
    op.drop_table("court_links")
    op.drop_table("court_blocks")
    op.drop_table("courts")
    op.drop_table("court_types")
    op.drop_table("venue_facilities")
    op.drop_table("venue_media")
    op.drop_table("venues")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
    op.drop_table("organizations")
    # drop enums
    for e in [
        "membershiptierscope",
        "usermembershipstatus",
        "orgmemberrole",
        "playerlevel",
        "dominanthand",
        "backhandtype",
        "discounttype",
    ]:
        sa.Enum(name=e).drop(op.get_bind(), checkfirst=True)
